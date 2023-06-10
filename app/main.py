import logging
import os
import requests

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from typing import Any, Dict, List

from cache.sqlite_cache import Cache
from config import vin_parquet_name, vin_table_name, vin_parquet_path, vpic_api_url
from database.connection import DatabaseConnection
from log.logger import logger
from utils import parse_response, structure_response


cache = Cache()
app = FastAPI()


@app.get("/lookup")
def lookup_vehicle_details(request: Request) -> Dict[str, Any]:
    """
    Checks the cache for the given vin to see if the vehicle details are present.
    If they aren't present, the vPIC API is queried to obtain the vehicle details and the result is cached.

    :param Request request: The FastAPI request object.
    :return: A dictionary containing the vehicle details.
    :rtype: dict
    :raises HTTPException 400: If the VIN is not a 17-character alphanumeric string.
    """

    vin = request.query_params.get("vin")

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


@app.delete("/remove")
def delete_vin_from_cache(request: Request) -> Dict[str, Any]:
    """
    Deletes the vin from the cache, if present, and returns a response indicating success or failure.

    :param Request request: The FastAPI request object.
    :return: A dictionary containing the vin and the cache deletion status.
    :rtype: dict
    :raises HTTPException 400: If the VIN is not a 17-character alphanumeric string.
    """
    vin = request.query_params.get("vin")
    if not len(vin) == 17 or not vin.isalnum():
        raise HTTPException(
            status_code=400,
            detail="VIN should be a 17 characters alpha-numeric string.",
        )

    delete_successful = cache.delete(vin)

    response = {"Input VIN Requested": vin, "Cache Delete Success?": delete_successful}

    return response


@app.get("/export")
def export_cache() -> Response:
    """
    Exports the cache as a parquet file with the name vin_parquet_name defined in config.py.

    :return: The HTTP response containing the exported Parquet file.
    :rtype: Response
    """
    convert_database_to_parquet()

    with open(vin_parquet_path, "rb") as file:
        data = file.read()
    headers = {
        "Content-Type": "application/octet-stream",
        "Content-Disposition": f"attachment; filename={vin_parquet_name}",
    }

    return Response(content=data, headers=headers)


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
        result = requests.get(request_url)
        if not result.status_code == 200:
            raise HTTPException(status_code=result.status_code, detail=result)
        results = result.json()["Results"]
    except Exception:
        logger.exception(
            "Encountered exception while making request to the vPIC API.",
            extra={"url": request_url},
        )
    return results


def convert_database_to_parquet() -> None:
    """
    Converts the database file into a parquet file.

    :raises Exception: If an error occurs during the conversion process.

    :rtype: None
    """
    database_engine = DatabaseConnection.get_engine()
    select_query = f"SELECT * FROM {vin_table_name}"
    try:
        vin_df = pd.read_sql_query(select_query, database_engine)
        vin_table = pa.Table.from_pandas(vin_df)
        pq.write_table(vin_table, vin_parquet_path)
    except Exception:
        logger.exception(
            "Encountered exception while converting database to parquet file."
        )
