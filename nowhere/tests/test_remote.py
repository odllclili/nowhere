from starlette.testclient import TestClient

from nowhere.remote import app


def test_remote_app_exposes_health_observer_and_mcp():
    paths = {getattr(route, "path", None) for route in app.routes}

    assert "/healthz" in paths
    assert "/mcp" in paths
    assert "/" in paths

    with TestClient(app) as client:
        health = client.get("/healthz")
        assert health.status_code == 200
        assert health.json() == {"ok": True, "service": "nowhere"}

        observer = client.get("/state")
        assert observer.status_code == 200
        assert "pos" in observer.json()
