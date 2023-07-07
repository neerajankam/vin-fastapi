from aiohttp import ClientError, ClientResponseError
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
def mock_response():
    with patch(module_path.format("Response")) as mock_response:
        yield mock_response


@pytest.fixture
def mock_session():
    with patch(module_path.format("aiohttp.ClientSession")) as mock_session:
        yield mock_session


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
def mock_build_response():
    with patch(module_path.format("build_response")) as mock_build_response:
        yield mock_build_response


class TestLookUpVehicleDetails:
    def setup_class(self):
        self.valid_vin = "1XP5DB9X7YN526158"

    async def test_vin_less_than_17_chars(self, mock_request):
        with pytest.raises(HTTPException) as http_exception:
            mock_request.query_params.get.return_value = "dummy_vin"
            await lookup_vehicle_details(mock_request)

        assert http_exception.value.status_code == 400
        assert (
            http_exception.value.detail
            == "VIN should be a 17 characters alpha-numeric string."
        )

    async def test_vin_not_alnum(self, mock_request):
        with pytest.raises(HTTPException) as http_exception:
            mock_request.query_params.get.return_value = "-----------------"
            await lookup_vehicle_details(mock_request)

        assert http_exception.value.status_code == 400
        assert len(mock_request.query_params.get.return_value) == 17
        assert (
            http_exception.value.detail
            == "VIN should be a 17 characters alpha-numeric string."
        )

    async def test_vin_in_cache(self, mock_cache, mock_request, mock_logger):
        mock_request.query_params.get.return_value = self.valid_vin
        mock_cache.get.return_value = {"dummy_key": "dummy_val"}
        result = await lookup_vehicle_details(mock_request)

        assert result == {"dummy_key": "dummy_val", "Cached Result?": True}

        mock_cache.get.assert_called_once_with(self.valid_vin)

    async def test_vin_not_in_cache(
        self,
        mock_cache,
        mock_request,
        mock_logger,
        mock_make_request,
        mock_build_response,
    ):
        mock_request.query_params.get.return_value = self.valid_vin
        mock_cache.get.return_value = None
        mock_make_request.return_value = {"dummy_key": "dummy_val"}
        mock_build_response.return_value = {"new_key": "new_val"}

        result = await lookup_vehicle_details(mock_request)

        assert result == {"new_key": "new_val", "Cached Result?": False}
        mock_cache.get.assert_called_once_with(self.valid_vin)
        mock_make_request.assert_called_once_with(self.valid_vin)
        mock_cache.set.assert_called_once_with(
            self.valid_vin, mock_build_response.return_value
        )
        mock_logger.debug.assert_any_call(
            f"No vehicle details present in the cache for {self.valid_vin}. Querying the vPIC API."
        )


class TestMakeRequest:
    def setup_class(self):
        self.valid_vin = "1XP5DB9X7YN526158"

    async def test_client_response_error(
        self, mock_session, mock_logger, mock_response
    ):
        mock_session.return_value.__aenter__.return_value.get.side_effect = (
            ClientResponseError
        )
        result = await make_request(self.valid_vin)
        assert result == mock_response.return_value
        mock_response.assert_called_once_with(
            content=str(
                "'coroutine' object does not support the asynchronous context manager protocol"
            ),
            status_code=500,
        )

    async def test_client_error(self, mock_session, mock_logger, mock_response):
        mock_session.return_value.__aenter__.return_value.get.side_effect = ClientError
        result = await make_request(self.valid_vin)
        assert result == mock_response.return_value
        mock_response.assert_called_once_with(
            content=str(
                "'coroutine' object does not support the asynchronous context manager protocol"
            ),
            status_code=500,
        )
        mock_logger.exception.assert_called_once_with(
            "Encountered exception while making request to https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/1XP5DB9X7YN526158?format=json"
        )

    async def test_exception(self, mock_session, mock_logger, mock_response):
        mock_session.return_value.__aenter__.return_value.get.side_effect = Exception
        result = await make_request(self.valid_vin)
        assert result == mock_response.return_value
        mock_response.assert_called_once_with(
            content=str(
                "'coroutine' object does not support the asynchronous context manager protocol"
            ),
            status_code=500,
        )
        mock_logger.exception.assert_called_once_with(
            "Encountered exception while making request to https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/1XP5DB9X7YN526158?format=json"
        )
