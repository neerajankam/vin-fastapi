import requests
from requests.exceptions import RequestException

from fastapi import APIRouter, HTTPException, Request
from typing import Any, Dict, List

from app.utils import parse_response, structure_response
from caching.sqlite_cache import cache
from app.config import vin_parquet_name, vin_table_name, vin_parquet_path, vpic_api_url
from log.logger import logger


router = APIRouter()


@router.get("/lookup")
def lookup_vehicle_details(request: Request) -> Dict[str, Any]:
    """
    Checks the cache for the given vin to see if the vehicle details are present.
    If they aren't present, the vPIC API is queried to obtain the vehicle details and the result is cached.

    :param Request request: The FastAPI request object.
    :return: A dictionary containing the vehicle details.
    :rtype: dict
    :raises HTTPException 400: If the VIN is not a 17-character alphanumeric string.
    """

    vin = request.query_params.get("vin", "")

    if not len(vin) == 17 or not vin.isalnum():
        raise HTTPException(
            status_code=400,
            detail="VIN should be a 17 characters alpha-numeric string.",
        )

    vehicle_details = cache.get(vin)
    present_in_cache = bool(vehicle_details)

    if not vehicle_details:
        logger.debug(
            f"No vehicle details present in the cache for {vin}. Querying the vPIC API."
        )
        vehicle_object = make_request(vin)
        vehicle_details = parse_response(vehicle_object)

    if not vehicle_details:
        raise HTTPException(
            status_code=404,
            detail=f"The API returned no valid values for the inputted vin: {vin}",
        )
    if not present_in_cache:
        cache.set(vin, vehicle_details)
    vehicle_details = structure_response(vehicle_details, vin, present_in_cache)
    logger.info(f"Vehicle details for the vin {vin} are {vehicle_details}")
    return vehicle_details


def make_request(vin) -> Dict[str, Any]:
    """
    Make a request to the vPIC API with the given vin and returns the response.

    :param vin: The VIN (Vehicle Identification Number) for the vehicle.
    :type vin: str
    :return: The response from the vPIC API as a dictionary.
    :rtype: Dict[str, Any]
    :raises HTTPException: If the Api doesn't return a successful response.
    :raises Exception: If an error occurs while making the request.
    """
    request_url = vpic_api_url.format(vin)

    try:
        response = requests.get(request_url)
    except RequestException:
        raise RequestException(
            "Encountered exception while making request to the vPIC API."
        )

    if not response.status_code == 200:
        raise HTTPException(status_code=response.status_code, detail=response)
    results = response.json()["Results"]

    return results
