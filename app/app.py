from fastapi import FastAPI
import requests

from cache.sqlite_cache import Cache
from models.parsing_models import  VinRequest
from utils import parse_response, structure_response


cache = Cache()
app = FastAPI()


@app.post("/lookup")
def lookup_vehicle_details(vin_object: VinRequest):
	vehicle_details = cache.get(vin_object.vin)
	present_in_cache = bool(vehicle_details)
	if not vehicle_details:
		vehicle_object = make_request(vin_object.vin)
		vehicle_details = parse_response(vehicle_object)
		cache.set(vin_object.vin, vehicle_details)
	vehicle_details = structure_response(vehicle_details, vin_object.vin, present_in_cache)
	return vehicle_details


def make_request(vin):
	vpic_api = f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{vin}?format=json"
	results = requests.get(vpic_api).json()["Results"]
	return results