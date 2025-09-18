from __future__ import annotations

from fastapi.testclient import TestClient

from ..main import app


def test_run_endpoint(monkeypatch) -> None:
    called = {}

    async def fake_run_pipeline(*, single_ticker=None, job_id=None):  # type: ignore[no-untyped-def]
        called["job_id"] = job_id

    monkeypatch.setenv("ADMIN_PASSWORD", "change_me")
    monkeypatch.setattr("app.backend.routes.run.run_pipeline", fake_run_pipeline)
    client = TestClient(app)
    response = client.post("/api/run", headers={"x-admin-password": "change_me"})
    assert response.status_code == 200
    assert "job_id" in response.json()
