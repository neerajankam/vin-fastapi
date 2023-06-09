import json

from models.parsing_models import VinResponse


def parse_response(vehicle_object):
	vehicle_details = dict()
	required_keys = {"Make", "Model", "Model Year", "Body Class"}
	for result in vehicle_object:
		current_key = result["Variable"]
		if current_key in required_keys:
			vehicle_details[current_key] = result["Value"]
	return vehicle_details

def structure_response(vehicle_details, vin, present_in_cache):
	final_response = VinResponse(
		vin=vin,
		make=vehicle_details["Make"],
		model=vehicle_details["Model"],
		year=vehicle_details["Model Year"],
		body_class=vehicle_details["Body Class"],
		cached_response=present_in_cache
	)
	return final_response
