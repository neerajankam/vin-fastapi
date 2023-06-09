from typing import Any, Dict, List

from models.parsing_models import VinResponse


def parse_response(vehicle_object: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Parses the response from the vPIC API and extracts the required vehicle details.

    :param vehicle_object: The response object from the vPIC API.
    :type vehicle_object: List[Dict[str, Any]]
    :return: A dictionary containing the parsed vehicle details.
    :rtype: Dict[str, Any]
    """
    vehicle_details = dict()
    required_keys = {"Make", "Model", "Model Year", "Body Class"}
    for result in vehicle_object:
        current_key = result["Variable"]
        if current_key in required_keys:
            vehicle_details[current_key] = result["Value"]

    return vehicle_details if any(vehicle_details.values()) else {}


def structure_response(
    vehicle_details: Dict[str, Any], vin: str, present_in_cache: bool
) -> VinResponse:
    """
    Structures the vehicle details into a VinResponse object.

    :param vehicle_details: The vehicle details dictionary.
    :type vehicle_details: Dict[str, Any]
    :param vin: The VIN for which the vehicle details are fetched.
    :type vin: str
    :param present_in_cache: Indicates whether the details are present in the cache.
    :type present_in_cache: bool
    :return: The structured response object containing the vehicle details.
    :rtype: VinResponse
    """
    final_response = VinResponse(
        input_vin_requested=vin,
        make=vehicle_details["Make"],
        model=vehicle_details["Model"],
        year=vehicle_details["Model Year"],
        body_class=vehicle_details["Body Class"],
        cached_response=present_in_cache,
    )

    return final_response
