import pytest
from fastapi import HTTPException
from unittest.mock import patch
from requests.exceptions import RequestException

from app.routers.lookup import lookup_vehicle_details, make_request
from app.config import vpic_api_url

module_path = "app.routers.lookup.{}"


@pytest.fixture
def mock_cache():
    with patch(module_path.format("cache")) as dummy_cache:
        yield dummy_cache


@pytest.fixture
def mock_request():
    with patch(module_path.format("Request")) as mock_request:
        yield mock_request


@pytest.fixture
def mock_requests():
    with patch(module_path.format("requests")) as mock_requests:
        yield mock_requests


@pytest.fixture
def mock_structure():
    with patch(module_path.format("structure_response")) as mock_structure:
        yield mock_structure


@pytest.fixture
def mock_logger():
    with patch(module_path.format("logger")) as mock_logger:
        yield mock_logger


@pytest.fixture
def mock_make_request():
    with patch(module_path.format("make_request")) as mock_make_request:
        yield mock_make_request


@pytest.fixture
def mock_parse_response():
    with patch(module_path.format("parse_response")) as mock_parse_response:
        yield mock_parse_response


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


class TestMakeRequest:
    def setup_class(self):
        self.valid_vin = "1XP5DB9X7YN526158"

    def test_exception_calling(self, mock_requests, mock_logger):
        mock_requests.get.side_effect = RequestException
        with pytest.raises(RequestException) as request_exception:
            make_request(self.valid_vin)
        assert (
            str(request_exception.value)
            == "Encountered exception while making request to the vPIC API."
        )

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
