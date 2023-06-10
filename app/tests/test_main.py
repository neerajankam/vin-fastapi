import pytest
from fastapi import HTTPException


from app.main import lookup_vehicle_details


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
