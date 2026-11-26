"""FastAPI application entrypoint with health checks, metrics, and Task CRUD API."""

import logging
import time
from typing import Dict, List
from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware

from . import __version__
from .config import Settings, get_settings
from .database import DatabaseManager
from .schemas import HealthResponse, TaskCreate, TaskResponse, TaskUpdate


def create_app(custom_settings: Settings | None = None) -> FastAPI:
    settings = custom_settings or get_settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format='{"timestamp":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}',
    )
    logger = logging.getLogger(settings.app_name)

    db = DatabaseManager(settings.database_url)
    metrics_state: Dict[str, float] = {
        "http_requests_total": 0,
        "http_errors_total": 0,
        "http_request_duration_seconds_sum": 0.0,
    }

    app = FastAPI(
        title="Three-Tier DevSecOps Platform API",
        version=__version__,
        description="Production-oriented FastAPI backend for EKS three-tier architecture.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    app.state.db = db
    app.state.settings = settings

    @app.on_event("startup")
    def on_startup() -> None:
        db.init_schema()
        logger.info("Initialized database schema for environment=%s", settings.app_env)

    @app.middleware("http")
    async def track_metrics(request: Request, call_next):
        start = time.perf_counter()
        metrics_state["http_requests_total"] += 1
        response = await call_next(request)
        elapsed = time.perf_counter() - start
        metrics_state["http_request_duration_seconds_sum"] += elapsed
        if response.status_code >= 500:
            metrics_state["http_errors_total"] += 1
        return response

    @app.get("/health/live", response_model=HealthResponse, tags=["Health"])
    def liveness_probe() -> HealthResponse:
        return HealthResponse(
            status="alive",
            environment=settings.app_env,
            version=__version__,
        )

    @app.get("/health/ready", response_model=HealthResponse, tags=["Health"])
    def readiness_probe(response: Response) -> HealthResponse:
        db_ok = db.check_health()
        if not db_ok:
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            return HealthResponse(
                status="not_ready",
                environment=settings.app_env,
                database="disconnected",
                version=__version__,
            )
        return HealthResponse(
            status="ready",
            environment=settings.app_env,
            database="connected",
            version=__version__,
        )

    @app.get("/metrics", tags=["Observability"])
    def prometheus_metrics() -> Response:
        db_up = 1 if db.check_health() else 0
        payload = "\n".join(
            [
                "# HELP http_requests_total Total HTTP requests handled by the API",
                "# TYPE http_requests_total counter",
                f'http_requests_total {int(metrics_state["http_requests_total"])}',
                "# HELP http_errors_total Total HTTP 5xx responses",
                "# TYPE http_errors_total counter",
                f'http_errors_total {int(metrics_state["http_errors_total"])}',
                "# HELP http_request_duration_seconds_sum Cumulative HTTP request duration in seconds",
                "# TYPE http_request_duration_seconds_sum counter",
                f'http_request_duration_seconds_sum {metrics_state["http_request_duration_seconds_sum"]:.6f}',
                "# HELP db_connection_status Database connectivity status (1=up, 0=down)",
                "# TYPE db_connection_status gauge",
                f"db_connection_status {db_up}",
                "",
            ]
        )
        return Response(content=payload, media_type="text/plain; version=0.0.4")

    @app.get("/api/v1/tasks", response_model=List[TaskResponse], tags=["Tasks"])
    def list_tasks() -> List[Dict]:
        return db.list_tasks()

    @app.post(
        "/api/v1/tasks",
        response_model=TaskResponse,
        status_code=status.HTTP_201_CREATED,
        tags=["Tasks"],
    )
    def create_task(payload: TaskCreate) -> Dict:
        return db.create_task(
            title=payload.title,
            description=payload.description or "",
            status=payload.status.value,
            priority=payload.priority.value,
            owner=payload.owner,
        )

    @app.get("/api/v1/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
    def get_task(task_id: int) -> Dict:
        task = db.get_task(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found",
            )
        return task

    @app.put("/api/v1/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
    def update_task(task_id: int, payload: TaskUpdate) -> Dict:
        updates = {
            "title": payload.title,
            "description": payload.description,
            "status": payload.status.value if payload.status else None,
            "priority": payload.priority.value if payload.priority else None,
            "owner": payload.owner,
        }
        updated = db.update_task(task_id, updates)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found",
            )
        return updated

    @app.delete(
        "/api/v1/tasks/{task_id}",
        status_code=status.HTTP_204_NO_CONTENT,
        tags=["Tasks"],
    )
    def delete_task(task_id: int) -> Response:
        deleted = db.delete_task(task_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found",
            )
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return app


app = create_app()
