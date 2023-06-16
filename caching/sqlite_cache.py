import json
import logging

from caching.cache_interface import CacheInterface
from database.connection import database
from models.database_models import Vin as VinDBModel


class Cache(CacheInterface):
    """
    Cache class for storing and retrieving vehicle details.

    Provides methods to get, set, and delete vehicle details from the cache.
    """

    __instance = None

    def __new__(cls, *args):
        if cls.__instance is None:
            cls.__instance = super(Cache, cls).__new__(cls)
        return cls.__instance

    def __init__(self, database):
        self.database = database

    def get(self, vin: str) -> dict:
        """
        Retrieves the vehicle details from the cache based on the provided VIN.

        :param vin: The VIN for which to retrieve the vehicle details.
        :type vin: str
        :return: The vehicle details retrieved from the cache.
        :rtype: dict
        """
        try:
            db_session = self.database.get_session()
            vin_object = db_session.query(VinDBModel).filter_by(vin=vin).one_or_none()
            vin_object = json.loads(vin_object.vehicle_details) if vin_object else {}
        except Exception:
            logging.exception(
                "Encountered exception while trying to fetch cache vin.",
                extra={"vin": vin},
            )
            vin_object = {}
        finally:
            db_session.close()
        return vin_object

    def set(self, vin: str, vehicle_details: dict):
        """
        Sets the vehicle details in the cache for the provided VIN.

        :param vin: The VIN for which to set the vehicle details.
        :type vin: str
        :param vehicle_details: The vehicle details to be stored in the cache.
        :type vehicle_details: dict
        """
        try:
            db_session = self.database.get_session()
            vehicle_details = VinDBModel(
                vin=vin, vehicle_details=json.dumps(vehicle_details)
            )
            db_session.add(vehicle_details)
            db_session.commit()
        except Exception:
            logging.exception(
                "Encountered exception while trying to cache vin.", extra={"vin": vin}
            )
            db_session.rollback()
        finally:
            db_session.close()

    def delete(self, vin: str) -> bool:
        """
        Deletes the vehicle details from the cache for the provided VIN.

        :param vin: The VIN for which to delete the vehicle details.
        :type vin: str
        :return: True if the deletion is successful, False otherwise.
        :rtype: bool
        """
        success = False
        try:
            db_session = self.database.get_session()
            deleted_rows = db_session.query(VinDBModel).filter_by(vin=vin).delete()
            db_session.commit()
            success = True if deleted_rows > 0 else False
        except Exception:
            logging.exception(
                "Encountered exception while trying to delete vin.", extra={"vin": vin}
            )
            db_session.rollback()
        finally:
            db_session.close()
            return success


cache = Cache(database)
