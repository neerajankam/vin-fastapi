import json
import logging

from database.connection import DatabaseConnection
from models.database_models import Vin as VinDBModel


class Cache:
	def __init__(self):
		self.db_connection = DatabaseConnection()

	def get(self, vin):
		try:
			vin_object = self.db_connection.query(VinDBModel).filter_by(vin=vin).one_or_none()
			vin_object = json.loads(vin_object.vehicle_details) if vin_object else {}
		except Exception:
			logging.exception("Encountered exception while trying to fetch cache vin.", extra={"vin": vin})
			vin_object = {}
		finally:
			self.db_connection.close()
		return vin_object

	def set(self, vin, vehicle_details):
		try:
			print("trying to set")
			# print(vin, vehicle_details)
			vehicle_details = VinDBModel(vin=vin, vehicle_details=json.dumps(vehicle_details))
			self.db_connection.add(vehicle_details)
			self.db_connection.commit()
		except Exception:
			logging.exception("Encountered exception while trying to cache vin.", extra={"vin": vin})
			self.db_connection.rollback()
		finally:
			self.db_connection.close()

	def delete(self, vin):
		success = False
		try:
			deleted_rows = self.db_connection.query(VinDBModel).filter_by(vin=vin).delete()
			print("Deleted rows: {}".format(deleted_rows))
			self.db_connection.commit()
		except Exception:
			success = False
			logging.exception("Encountered exception while trying to delete vin.", extra={"vin":vin})
			self.db_connection.rollback()
		finally:
			self.db_connection.close()
			success = True if deleted_rows == 1 else False
			return success
