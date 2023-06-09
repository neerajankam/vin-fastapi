import logging
import os
import requests

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from cache.sqlite_cache import Cache
from config import vin_parquet_name, vin_table_name, vin_parquet_path, vpic_api_url
from database.connection import DatabaseConnection
from utils import parse_response, structure_response


cache = Cache()
app = FastAPI()

@app.get("/lookup")
def lookup_vehicle_details(request: Request):
	vin = request.query_params.get("vin")
	if not len(vin) == 17 or not vin.isalnum():
		raise HTTPException(status_code=400, detail="VIN should be a 17 characters alpha-numeric string.")

	vehicle_details = cache.get(vin)
	present_in_cache = bool(vehicle_details)
	if not vehicle_details:
		vehicle_object = make_request(vin)
		vehicle_details = parse_response(vehicle_object)
		cache.set(vin, vehicle_details)
	vehicle_details = structure_response(vehicle_details, vin, present_in_cache)
	return vehicle_details

@app.delete("/remove")
def delete_vin_from_cache(request: Request):
	vin = request.query_params.get("vin")
	if not len(vin) == 17 or not vin.isalnum():
		raise HTTPException(status_code=400, detail="VIN should be a 17 characters alpha-numeric string.")
	delete_successful = cache.delete(vin)
	response = {
	    "Input VIN Requested": vin,
	    "Cache Delete Success?": delete_successful
	}
	return response

@app.get("/export")
def export_cache():
	convert_database_to_parquet()

	with open(vin_parquet_path, "rb") as file:
		data = file.read()
	headers = {
		"Content-Type": "application/octet-stream",
		"Content-Disposition": f"attachment; filename={vin_parquet_name}"
	}

	return Response(content=data, headers=headers)

def make_request(vin):
	vpic_api_url = vpic_api_url.format(vin)
	results = requests.get(vpic_api_url).json()["Results"]
	return results

def convert_database_to_parquet():
	database_engine = DatabaseConnection.get_engine()
	select_query = f"SELECT * FROM {vin_table_name}"
	vin_df = pd.read_sql_query(select_query, database_engine)
	vin_table = pa.Table.from_pandas(vin_df)
	pq.write_table(vin_table, vin_parquet_path)
