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
    with patch(module_path.format("DatabaseConnection")) as mock_database_connection:
        yield mock_database_connection


@pytest.fixture
def mock_pandas():
    with patch(module_path.format("pd")) as mock_pandas:
        yield mock_pandas


@pytest.fixture
def mock_arrow():
    with patch(module_path.format("pa")) as mock_arrow:
        yield mock_arrow


@pytest.fixture
def mock_parquet():
    with patch(module_path.format("pq")) as mock_parquet:
        yield mock_parquet


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

    def test_failure(self, mock_os):
        with pytest.raises(FileNotFoundError) as file_error:
            mock_os.path.exists.return_value = False
            export_cache()
        assert (
            str(file_error.value)
            == f"Database parquet file not found at {vin_parquet_path}"
        )


class TestConvertDatabaseToParquet:
    def test_success(
        self,
        mock_database_connection,
        mock_pandas,
        mock_arrow,
        mock_parquet,
    ):
        mock_pandas.read_sql_query.return_value = []
        mock_arrow.Table.from_pandas.return_value = None
        convert_database_to_parquet()
        mock_pandas.read_sql_query.assert_called_once_with(
            f"SELECT * FROM {vin_table_name}",
            mock_database_connection.get_engine.return_value,
        )
        mock_arrow.Table.from_pandas.assert_called_once_with(
            mock_pandas.read_sql_query.return_value
        )
        mock_parquet.write_table.assert_called_once_with(
            mock_arrow.Table.from_pandas.return_value, vin_parquet_path
        )

    def test_failure(self, mock_database_connection, mock_pandas):
        with pytest.raises(DatabaseToParquetError) as conversion_error:
            mock_pandas.read_sql_query.side_effect = Exception
            convert_database_to_parquet()
        assert (
            str(conversion_error.value)
            == "Encountered exception while converting database to parquet file."
        )
