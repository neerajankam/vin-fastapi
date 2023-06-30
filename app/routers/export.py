import os
import pandas as pd
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response

from app.config import vin_parquet_name, vin_table_name, vin_parquet_path
from database.connection import Database
from log.logger import logger

router = APIRouter()


@router.get("/export")
def export_cache() -> Response:
    """
    Exports the cache as a parquet file with the name vin_parquet_name defined in config.py.

    :return: The HTTP response containing the exported Parquet file.
    :rtype: Response
    """
    try:
        convert_database_to_parquet()
    except DatabaseToParquetError as e:
        logger.exception(
            "Encountered exception while converting database to parquet file."
        )
        raise HTTPException(detail=str(e), status_code=500)
    try:
        file_chunks = generate_file_chunks(vin_parquet_path)
    except FileNotFoundError:
        logger.exception("Database parquet file has not been found.")
        raise HTTPException(
            detail="Database parquet file has not been found.", status_code=404
        )
    content = b"".join(file_chunks)

    headers = {
        "Content-Type": "application/octet-stream",
        "Content-Disposition": f"attachment; filename={vin_parquet_name}",
    }

    return Response(content=content, headers=headers)


def generate_file_chunks(file_path, chunk_size=4096):
    with open(file_path, "rb") as file:
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            yield chunk


def convert_database_to_parquet() -> None:
    """
    Converts the database file into a parquet file.

    :raises Exception: If an error occurs during the conversion process.

    :rtype: None
    """
    database_engine = Database.get_engine()
    select_query = f"SELECT * FROM {vin_table_name}"

    try:
        vin_df = pd.read_sql_query(select_query, database_engine)
        vin_df.to_parquet(vin_parquet_path)
    except Exception:
        raise DatabaseToParquetError(
            "Encountered exception while converting database to parquet file."
        )


class DatabaseToParquetError(Exception):
    pass
