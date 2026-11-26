"""Database abstraction supporting PostgreSQL (Amazon RDS / local) and SQLite (tests)."""

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Dict, Generator, List, Optional
from urllib.parse import urlparse

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:  # pragma: no cover - optional in lightweight test environments
    psycopg2 = None
    RealDictCursor = None


class DatabaseManager:
    """Manages connections and CRUD operations for PostgreSQL or SQLite."""

    def __init__(self, database_url: str) -> None:
        self.database_url = database_url
        self.is_postgres = database_url.startswith("postgresql://") or database_url.startswith(
            "postgres://"
        )
        if self.is_postgres and psycopg2 is None:
            raise RuntimeError(
                "psycopg2-binary is required when DATABASE_URL uses PostgreSQL"
            )

    @contextmanager
    def connection(self) -> Generator[Any, None, None]:
        if self.is_postgres:
            conn = psycopg2.connect(self.database_url, connect_timeout=5)
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()
        else:
            parsed = urlparse(self.database_url)
            db_path = parsed.path if parsed.path else "local_dev.db"
            if self.database_url.startswith("sqlite:///"):
                db_path = self.database_url[len("sqlite:///"):]
            conn = sqlite3.connect(db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()

    def init_schema(self) -> None:
        create_pg = """
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title VARCHAR(120) NOT NULL,
            description VARCHAR(500) NOT NULL DEFAULT '',
            status VARCHAR(32) NOT NULL DEFAULT 'open',
            priority VARCHAR(32) NOT NULL DEFAULT 'medium',
            owner VARCHAR(60) NOT NULL DEFAULT 'platform-team',
            created_at TIMESTAMPTZ NOT NULL,
            updated_at TIMESTAMPTZ NOT NULL
        );
        """
        create_sqlite = """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'open',
            priority TEXT NOT NULL DEFAULT 'medium',
            owner TEXT NOT NULL DEFAULT 'platform-team',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """
        with self.connection() as conn:
            cur = conn.cursor()
            cur.execute(create_pg if self.is_postgres else create_sqlite)

    def check_health(self) -> bool:
        try:
            with self.connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT 1")
                cur.fetchone()
            return True
        except Exception:
            return False

    def list_tasks(self) -> List[Dict[str, Any]]:
        query = (
            "SELECT id, title, description, status, priority, owner, created_at, updated_at "
            "FROM tasks ORDER BY id DESC"
        )
        with self.connection() as conn:
            if self.is_postgres:
                cur = conn.cursor(cursor_factory=RealDictCursor)
                cur.execute(query)
                return [dict(row) for row in cur.fetchall()]
            cur = conn.cursor()
            cur.execute(query)
            return [dict(row) for row in cur.fetchall()]

    def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        placeholder = "%s" if self.is_postgres else "?"
        query = (
            "SELECT id, title, description, status, priority, owner, created_at, updated_at "
            f"FROM tasks WHERE id = {placeholder}"
        )
        with self.connection() as conn:
            if self.is_postgres:
                cur = conn.cursor(cursor_factory=RealDictCursor)
                cur.execute(query, (task_id,))
                row = cur.fetchone()
                return dict(row) if row else None
            cur = conn.cursor()
            cur.execute(query, (task_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def create_task(
        self,
        title: str,
        description: str,
        status: str,
        priority: str,
        owner: str,
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        if self.is_postgres:
            query = """
            INSERT INTO tasks (title, description, status, priority, owner, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id, title, description, status, priority, owner, created_at, updated_at
            """
            with self.connection() as conn:
                cur = conn.cursor(cursor_factory=RealDictCursor)
                cur.execute(query, (title, description, status, priority, owner, now, now))
                return dict(cur.fetchone())

        query = """
        INSERT INTO tasks (title, description, status, priority, owner, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        with self.connection() as conn:
            cur = conn.cursor()
            cur.execute(query, (title, description, status, priority, owner, now, now))
            new_id = cur.lastrowid
        created = self.get_task(int(new_id))
        assert created is not None
        return created

    def update_task(self, task_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        existing = self.get_task(task_id)
        if not existing:
            return None

        merged = {
            "title": updates.get("title") if updates.get("title") is not None else existing["title"],
            "description": (
                updates.get("description")
                if updates.get("description") is not None
                else existing["description"]
            ),
            "status": (
                updates.get("status") if updates.get("status") is not None else existing["status"]
            ),
            "priority": (
                updates.get("priority")
                if updates.get("priority") is not None
                else existing["priority"]
            ),
            "owner": updates.get("owner") if updates.get("owner") is not None else existing["owner"],
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        if self.is_postgres:
            query = """
            UPDATE tasks
            SET title = %s, description = %s, status = %s, priority = %s, owner = %s, updated_at = %s
            WHERE id = %s
            RETURNING id, title, description, status, priority, owner, created_at, updated_at
            """
            with self.connection() as conn:
                cur = conn.cursor(cursor_factory=RealDictCursor)
                cur.execute(
                    query,
                    (
                        merged["title"],
                        merged["description"],
                        merged["status"],
                        merged["priority"],
                        merged["owner"],
                        merged["updated_at"],
                        task_id,
                    ),
                )
                row = cur.fetchone()
                return dict(row) if row else None

        query = """
        UPDATE tasks
        SET title = ?, description = ?, status = ?, priority = ?, owner = ?, updated_at = ?
        WHERE id = ?
        """
        with self.connection() as conn:
            cur = conn.cursor()
            cur.execute(
                query,
                (
                    merged["title"],
                    merged["description"],
                    merged["status"],
                    merged["priority"],
                    merged["owner"],
                    merged["updated_at"],
                    task_id,
                ),
            )
        return self.get_task(task_id)

    def delete_task(self, task_id: int) -> bool:
        placeholder = "%s" if self.is_postgres else "?"
        query = f"DELETE FROM tasks WHERE id = {placeholder}"
        with self.connection() as conn:
            cur = conn.cursor()
            cur.execute(query, (task_id,))
            return cur.rowcount > 0
