import pytest
from unittest.mock import patch

from app.routers.export import (
    export_cache,
    convert_database_to_parquet,
    DatabaseToParquetError,
)
from app.config import vin_parquet_name, vin_table_name, vin_parquet_path

module_path = "app.routers.export.{}"


@pytest.fixture
def mock_convert_database():
    with patch(
        module_path.format("convert_database_to_parquet")
    ) as mock_convert_database:
        yield mock_convert_database


@pytest.fixture
def mock_response():
    with patch(module_path.format("Response")) as mock_response:
        yield mock_response


@pytest.fixture
def mock_os():
    with patch(module_path.format("os")) as mock_os:
        yield mock_os


@pytest.fixture
def mock_database_connection():
    with patch(module_path.format("Database")) as mock_database_connection:
        yield mock_database_connection


@pytest.fixture
def mock_logger():
    with patch(module_path.format("logger")) as mock_logger:
        yield mock_logger


@pytest.fixture
def mock_pandas():
    with patch(module_path.format("pd")) as mock_pandas:
        yield mock_pandas


@pytest.fixture
def mock_generate():
    with patch(module_path.format("generate_file_chunks")) as mock_generate:
        yield mock_generate


class TestExportCache:
    def test_success(
        self, mock_convert_database, mock_response, mock_generate, mock_os
    ):
        mock_os.path.exists.return_value = True
        mock_generate.return_value = [b"random_string", b"random_string2"]
        result = export_cache()
        mock_convert_database.assert_called_once()
        assert result == mock_response.return_value
        mock_response.assert_called_once_with(
            content=b"random_stringrandom_string2",
            headers={
                "Content-Type": "application/octet-stream",
                "Content-Disposition": "attachment; filename=vin_cache.parquet",
            },
        )

    def test_no_parquet_path(self, mock_os, mock_response):
        mock_os.path.exists.return_value = False
        result = export_cache()
        assert result == mock_response.return_value
        mock_response.assert_called_once_with(
            content="Database parquet file has not been found", status_code=404
        )

    def test_database_to_parquet_error(self, mock_logger, mock_response, mock_pandas):
        mock_pandas.read_sql_query.side_effect = Exception
        result = export_cache()
        mock_logger.exception.assert_called_once_with(
            "Encountered exception while converting database to parquet file."
        )
        assert result == mock_response.return_value
        mock_response.assert_called_once_with(
            content="Encountered exception while converting database to parquet file.",
            status_code=500,
        )


class TestConvertDatabaseToParquet:
    def test_success(self, mock_database_connection, mock_pandas):
        convert_database_to_parquet()
        mock_pandas.read_sql_query.assert_called_once_with(
            f"SELECT * FROM {vin_table_name}",
            mock_database_connection.get_engine.return_value,
        )
        mock_pandas.read_sql_query.return_value.to_parquet.assert_called_once_with(
            vin_parquet_path
        )

    def test_failure(self, mock_database_connection, mock_pandas):
        with pytest.raises(DatabaseToParquetError) as conversion_error:
            mock_pandas.read_sql_query.side_effect = Exception
            convert_database_to_parquet()
        assert (
            str(conversion_error.value)
            == "Encountered exception while converting database to parquet file."
        )
