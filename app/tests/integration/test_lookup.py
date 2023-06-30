import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


from app.main import app
from app.routers.lookup import cache

module_path = "app.routers.lookup.{}"
client = TestClient(app)


@pytest.fixture
def mock_cache():
    with patch(module_path.format("cache")) as mock_cache:
        yield mock_cache


@pytest.fixture
def mock_make_request():
    with patch(module_path.format("make_request")) as mock_make_request:
        yield mock_make_request


class TestLookupVehicleDetails:
    def test_cached_result(self, mock_cache, mocker):
        vin = "ABC1234567890DEF0"
        mock_cache = MagicMock()
        mock_cache.get.return_value = {
            "VIN": vin,
            "Make": "Ford",
            "Model": "Mustang",
            "Year": 2021,
            "Cached Result?": True,
        }

        mocker.patch.object(cache, "get", mock_cache.get)
        response = client.get(f"/lookup?vin={vin}")
        assert response.status_code == 200
        assert response.json() == {
            "VIN": vin,
            "Make": "Ford",
            "Model": "Mustang",
            "Year": 2021,
            "Cached Result?": True,
        }
        mock_cache.get.assert_called_once_with(vin)

    def test_invalid_vin(self, mock_cache, mock_make_request):
        vin = "InvalidVIN"
        response = client.get(f"/lookup?vin={vin}")
        assert response.status_code == 400
        assert response.json() == {
            "detail": "VIN should be a 17 characters alpha-numeric string."
        }
        mock_cache.get.assert_not_called()
        mock_make_request.assert_not_called()
