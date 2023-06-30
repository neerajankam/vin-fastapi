from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_export_cache():
    response = client.get("/export")

    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/octet-stream"
    assert "Content-Disposition" in response.headers
    assert response.headers["Content-Disposition"].startswith("attachment; filename=")
    assert response.content is not None
