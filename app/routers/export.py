import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response

from app.config import vin_parquet_name, vin_table_name, vin_parquet_path
from database.connection import DatabaseConnection


router = APIRouter()


@router.get("/export")
def export_cache() -> Response:
    """
    Exports the cache as a parquet file with the name vin_parquet_name defined in config.py.

    :return: The HTTP response containing the exported Parquet file.
    :rtype: Response
    """
    convert_database_to_parquet()
    if not os.path.exists(vin_parquet_path):
        raise FileNotFoundError(
            f"Database parquet file not found at {vin_parquet_path}"
        )

    with open(vin_parquet_path, "rb") as file:
        data = file.read()
    headers = {
        "Content-Type": "application/octet-stream",
        "Content-Disposition": f"attachment; filename={vin_parquet_name}",
    }

    return Response(content=data, headers=headers)


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
        raise DatabaseToParquetError(
            "Encountered exception while converting database to parquet file."
        )


class DatabaseToParquetError(Exception):
    pass
