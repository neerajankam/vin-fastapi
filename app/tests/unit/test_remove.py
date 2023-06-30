import pytest
from fastapi import HTTPException
from unittest.mock import patch

from app.routers.remove import delete_vin_from_cache

module_path = "app.routers.remove.{}"


@pytest.fixture
def mock_cache():
    with patch(module_path.format("cache")) as dummy_cache:
        yield dummy_cache


@pytest.fixture
def mock_request():
    with patch(module_path.format("Request")) as mock_request:
        yield mock_request


class TestDeleteVinFromCache:
    def setup_class(self):
        self.valid_vin = "1XP5DB9X7YN526158"

    def test_vin_less_than_17_chars(self, mock_request):
        with pytest.raises(HTTPException) as http_exception:
            mock_request.query_params.get.return_value = "dummy_vin"
            delete_vin_from_cache(mock_request)

        assert http_exception.value.status_code == 400
        assert (
            http_exception.value.detail
            == "VIN should be a 17 characters alpha-numeric string."
        )

    def test_delete_success(self, mock_request, mock_cache):
        mock_request.query_params.get.return_value = self.valid_vin
        result = delete_vin_from_cache(mock_request)
        mock_cache.delete.assert_called_once_with(
            mock_request.query_params.get.return_value
        )
        assert result == {
            "Input VIN Requested": mock_request.query_params.get.return_value,
            "Cache Delete Success?": mock_cache.delete.return_value,
        }
