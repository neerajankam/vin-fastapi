import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app
from app.routers.export import convert_database_to_parquet, DatabaseToParquetError


client = TestClient(app, raise_server_exceptions=False)
module_path = "app.routers.export.{}"


@pytest.fixture
def mock_convert_database():
    with patch(
        module_path.format("convert_database_to_parquet")
    ) as mock_convert_database:
        yield mock_convert_database


@pytest.fixture
def mock_logger():
    with patch(module_path.format("logger")) as mock_logger:
        yield mock_logger


class TestExportCache:
    def test_success(self):
        response = client.get("/export")

        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/octet-stream"
        assert "Content-Disposition" in response.headers
        assert response.headers["Content-Disposition"].startswith(
            "attachment; filename="
        )
        assert response.content is not None

    def test_exception(self, mocker, mock_convert_database, mock_logger):
        mock_object = MagicMock()
        mock_object.side_effect = DatabaseToParquetError
        mocker.patch(convert_database_to_parquet).side_effect = DatabaseToParquetError
        response = client.get("/export")
        assert response.content == ""
        assert (
            http_exception.value.detail == "Database parquet file has not been found."
        )
        assert http_exception.value.status_code == 404
        mock_logger.exception.assert_called_once_with(
            "Database parquet file has not been found."
        )
