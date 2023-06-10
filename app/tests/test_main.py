import pytest
from fastapi import HTTPException
from requests.exceptions import RequestException

from app.main import (
    lookup_vehicle_details,
    delete_vin_from_cache,
    export_cache,
    make_request,
    convert_database_to_parquet,
    DatabaseToParquetError,
)
from app.config import vin_parquet_path, vin_table_name, vpic_api_url


module_path = "app.main.{}"


class TestLookUpVehicleDetails:
    def setup_class(self):
        self.valid_vin = "1XP5DB9X7YN526158"

    def test_vin_less_than_17_chars(self, mock_request):
        with pytest.raises(HTTPException) as http_exception:
            mock_request.query_params.get.return_value = "dummy_vin"
            lookup_vehicle_details(mock_request)

        assert http_exception.value.status_code == 400
        assert (
            http_exception.value.detail
            == "VIN should be a 17 characters alpha-numeric string."
        )

    def test_vin_not_alnum(self, mock_request):
        with pytest.raises(HTTPException) as http_exception:
            mock_request.query_params.get.return_value = "-----------------"
            lookup_vehicle_details(mock_request)

        assert http_exception.value.status_code == 400
        assert len(mock_request.query_params.get.return_value) == 17
        assert (
            http_exception.value.detail
            == "VIN should be a 17 characters alpha-numeric string."
        )

    def test_vin_in_cache(self, mock_cache, mock_request, mock_structure, mock_logger):
        mock_request.query_params.get.return_value = self.valid_vin
        mock_cache.get.return_value = {"dummy_key": "dummy_val"}
        result = lookup_vehicle_details(mock_request)

        assert result == mock_structure.return_value

        mock_cache.get.assert_called_once_with(self.valid_vin)
        mock_structure.assert_called_once_with(
            mock_cache.get.return_value,
            mock_request.query_params.get.return_value,
            True,
        )
        mock_logger.info.assert_called_once_with(
            f"Vehicle details for the vin {self.valid_vin} are {mock_structure.return_value}"
        )

    def test_vin_not_in_cache(
        self,
        mock_cache,
        mock_request,
        mock_structure,
        mock_logger,
        mock_make_request,
        mock_parse_response,
    ):
        mock_request.query_params.get.return_value = self.valid_vin
        mock_cache.get.return_value = None
        mock_make_request.return_value = {"dummy_key": "dummy_val"}
        mock_parse_response.return_value = "parsed_response"

        result = lookup_vehicle_details(mock_request)

        assert result == mock_structure.return_value
        mock_cache.get.assert_called_once_with(self.valid_vin)
        mock_make_request.assert_called_once_with(self.valid_vin)
        mock_parse_response.assert_called_once_with(mock_make_request.return_value)
        mock_cache.set.assert_called_once_with(
            self.valid_vin, mock_parse_response.return_value
        )
        mock_structure.assert_called_once_with(
            mock_parse_response.return_value,
            self.valid_vin,
            False,
        )
        mock_logger.debug.assert_any_call(
            f"No vehicle details present in the cache for {self.valid_vin}. Querying the vPIC API."
        )
        mock_logger.info.assert_any_call(
            f"Vehicle details for the vin {self.valid_vin} are {mock_structure.return_value}"
        )


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


class TestExportCache:
    def test_success(self, mock_convert_database, mocker, mock_response):
        # Note that mocker fixture is provided by pytest-mock module.
        mocker.patch("builtins.open", mocker.mock_open(read_data="Mocked content"))
        result = export_cache()
        mock_convert_database.assert_called_once()
        assert result == mock_response.return_value
        mock_response.assert_called_once_with(
            content="Mocked content",
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


class TestMakeRequest:
    def setup_class(self):
        self.valid_vin = "1XP5DB9X7YN526158"

    def test_exception_calling(self, mock_requests, mock_logger):
        mock_requests.get.side_effect = RequestException
        result = make_request(self.valid_vin)
        mock_logger.exception.assert_called_once_with(
            "Encountered exception while making request to the vPIC API.",
            extra={"url": vpic_api_url.format(self.valid_vin)},
        )
        assert result == []

    def test_status_code_not_200(self, mock_requests):
        with pytest.raises(HTTPException) as http_exception:
            mock_requests.get.return_value.status_code = 400
            make_request(self.valid_vin)

        assert http_exception.value.status_code == 400
        assert http_exception.value.detail == mock_requests.get.return_value

    def test_status_code_200(self, mock_requests, mock_logger):
        mock_requests.get.return_value.status_code = 200
        mock_requests.get.return_value.json.return_value = {"Results": ["dummy_result"]}
        result = make_request(self.valid_vin)
        mock_logger.exception.assert_not_called()
        mock_requests.get.return_value.json.assert_called_once()
        assert result == ["dummy_result"]


class TestConvertDatabaseToParquet:
    def test_success(
        self,
        mock_database_connection,
        mock_pandas,
        mock_arrow,
        mock_logger,
        mock_parquet,
    ):
        mock_pandas.read_sql_query.return_value = []
        mock_arrow.Table.from_pandas.return_value = None
        convert_database_to_parquet()
        mock_logger.exception.assert_not_called()
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
