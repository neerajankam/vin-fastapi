from typing import Any, Dict, List

from models.parsing_models import VinResponse


def build_response(vehicle_object: List[Dict[str, Any]], vin: str) -> Dict[str, Any]:
    """
    Parses the response from the vPIC API and extracts the required vehicle details.

    :param vehicle_object: The response object from the vPIC API.
    :type vehicle_object: List[Dict[str, Any]]
    :param vin: The VIN for which the vehicle details are fetched.
    :type vin: str
    :return: A dictionary containing the parsed vehicle details.
    :rtype: Dict[str, Any]
    """
    if not vehicle_object:
        return {}
    vehicle_details = dict()
    required_keys = {"Make", "Model", "Model Year", "Body Class"}
    for result in vehicle_object:
        current_key = result["Variable"]
        if current_key in required_keys:
            vehicle_details[current_key] = result["Value"]

    if not any(vehicle_details.values()):
        return {}

    vehicle_details["Input VIN Requested"] = vin

    return vehicle_details
