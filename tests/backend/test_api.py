"""Unit tests for FastAPI backend endpoints and validation."""

import os
import sys
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parents[2] / "application" / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.config import Settings  # noqa: E402
from app.main import create_app  # noqa: E402


class TestBackendAPI(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        db_file = os.path.join(self.tmp_dir.name, "test_api.db")
        settings = Settings(
            app_name="test-api",
            app_env="test",
            log_level="WARNING",
            database_url=f"sqlite:///{db_file}",
            allowed_origins_raw="http://localhost:3000",
        )
        self.app = create_app(custom_settings=settings)
        self.client_cm = TestClient(self.app)
        self.client = self.client_cm.__enter__()

    def tearDown(self) -> None:
        self.client_cm.__exit__(None, None, None)
        self.tmp_dir.cleanup()

    def test_liveness_and_readiness(self) -> None:
        live = self.client.get("/health/live")
        self.assertEqual(live.status_code, 200)
        self.assertEqual(live.json()["status"], "alive")

        ready = self.client.get("/health/ready")
        self.assertEqual(ready.status_code, 200)
        self.assertEqual(ready.json()["status"], "ready")
        self.assertEqual(ready.json()["database"], "connected")

    def test_metrics_endpoint(self) -> None:
        self.client.get("/health/live")
        metrics = self.client.get("/metrics")
        self.assertEqual(metrics.status_code, 200)
        self.assertIn("http_requests_total", metrics.text)
        self.assertIn("db_connection_status 1", metrics.text)

    def test_task_crud_lifecycle(self) -> None:
        create_resp = self.client.post(
            "/api/v1/tasks",
            json={
                "title": "Enable Trivy SARIF upload",
                "description": "Upload container scan findings to GitHub Security tab",
                "priority": "high",
                "owner": "devsecops",
            },
        )
        self.assertEqual(create_resp.status_code, 201)
        created = create_resp.json()
        task_id = created["id"]
        self.assertEqual(created["status"], "open")

        list_resp = self.client.get("/api/v1/tasks")
        self.assertEqual(list_resp.status_code, 200)
        self.assertEqual(len(list_resp.json()), 1)

        update_resp = self.client.put(
            f"/api/v1/tasks/{task_id}",
            json={"status": "completed", "priority": "critical"},
        )
        self.assertEqual(update_resp.status_code, 200)
        self.assertEqual(update_resp.json()["status"], "completed")
        self.assertEqual(update_resp.json()["priority"], "critical")

        delete_resp = self.client.delete(f"/api/v1/tasks/{task_id}")
        self.assertEqual(delete_resp.status_code, 204)

        missing_resp = self.client.get(f"/api/v1/tasks/{task_id}")
        self.assertEqual(missing_resp.status_code, 404)

    def test_validation_rejects_short_title(self) -> None:
        resp = self.client.post("/api/v1/tasks", json={"title": "A"})
        self.assertEqual(resp.status_code, 422)


if __name__ == "__main__":
    unittest.main()
