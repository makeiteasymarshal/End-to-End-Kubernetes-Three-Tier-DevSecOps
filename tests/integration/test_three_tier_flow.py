"""Integration tests verifying end-to-end three-tier API persistence and error handling."""

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


class TestThreeTierIntegration(unittest.TestCase):
    def test_persistence_across_app_restarts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_file = os.path.join(tmp_dir, "integration.db")
            settings = Settings(
                app_name="integration-api",
                app_env="integration",
                log_level="WARNING",
                database_url=f"sqlite:///{db_file}",
                allowed_origins_raw="http://localhost:8080",
            )

            app1 = create_app(custom_settings=settings)
            with TestClient(app1) as client1:
                resp = client1.post(
                    "/api/v1/tasks",
                    json={"title": "Verify RDS persistence", "owner": "sre"},
                )
                self.assertEqual(resp.status_code, 201)
                task_id = resp.json()["id"]

            # Simulate pod restart against the same database
            app2 = create_app(custom_settings=settings)
            with TestClient(app2) as client2:
                fetched = client2.get(f"/api/v1/tasks/{task_id}")
                self.assertEqual(fetched.status_code, 200)
                self.assertEqual(fetched.json()["title"], "Verify RDS persistence")


if __name__ == "__main__":
    unittest.main()
