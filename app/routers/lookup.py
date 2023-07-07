import requests
from requests.exceptions import RequestException

import aiohttp
from aiohttp import ClientError, ClientResponseError
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response
from typing import Any, Dict, List

from app.utils import build_response
from caching.sqlite_cache import cache
from app.config import vin_parquet_name, vin_table_name, vin_parquet_path, vpic_api_url
from log.logger import logger


router = APIRouter()


@router.get("/lookup")
async def lookup_vehicle_details(request: Request) -> Dict[str, Any]:
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
    if vehicle_details:
        vehicle_details["Cached Result?"] = True
        return vehicle_details

    logger.debug(
        f"No vehicle details present in the cache for {vin}. Querying the vPIC API."
    )
    vehicle_object = await make_request(vin)
    vehicle_details = build_response(vehicle_object, vin)

    if not vehicle_details:
        raise HTTPException(
            status_code=404,
            detail=f"The API returned no valid values for the inputted vin: {vin}",
        )
    cache.set(vin, vehicle_details)
    vehicle_details["Cached Result?"] = False

    return vehicle_details


async def make_request(vin: str) -> Dict[str, Any]:
    """
    Makes an HTTP GET request to the vPIC API with the given VIN (Vehicle Identification Number).

    :param vin: The VIN (Vehicle Identification Number) for the vehicle.
    :type vin: str
    :return: The response from the vPIC API as a dictionary.
    :rtype: Dict[str, Any]
    :raises ClientResponseError: If an error occurs during the request.
    :raises ClientError: If an error occurs during the request.
    :raises Exception: If an exception occurs during the request.
    """
    url = vpic_api_url.format(vin)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response_json = await response.json()
                response.raise_for_status()

        response_json = await response.json()
        return response_json["Results"]
    except ClientResponseError as e:
        return Response(content=str(e), status_code=response.status)
    except ClientError as e:
        logger.exception(f"Error while making the request to {url}")
        return Response(content=str(e), status_code=response.status)
    except Exception as e:
        logger.exception(f"Encountered exception while making request to {url}")
        return Response(content=str(e), status_code=500)
