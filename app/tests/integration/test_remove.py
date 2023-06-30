import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app

client = TestClient(app)


class TestDeleteVinFromCache:
    def test_success(self):
        response = client.delete("/remove?vin=ABC1234567890DEF0")
        assert response.status_code == 200
        assert response.json() == {
            "Input VIN Requested": "ABC1234567890DEF0",
            "Cache Delete Success?": False,
        }

    def test_exception(self):
        response = client.delete("/remove?vin=InvalidVIN")
        assert response.status_code == 400
        assert response.json() == {
            "detail": "VIN should be a 17 characters alpha-numeric string."
        }
