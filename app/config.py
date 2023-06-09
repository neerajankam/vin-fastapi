import os

from models.database_models import Vin

HERE = os.path.dirname(os.path.abspath(__file__))

# App configuration
vin_parquet_name = "vin_cache.parquet"
vin_table_name = Vin.__table__.name
vin_parquet_path = os.path.join(HERE, "..", "data", vin_parquet_name)
vpic_api_url = "https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{}?format=json"
