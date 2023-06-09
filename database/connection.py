from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from alembic import op


DATABASE_PATH = "sqlite:////Users/neerajankam/Desktop/koffie_labs_challenge/data/vins_database.db"


class DatabaseConnection:
	__instance = None
	__engine = None
	def __new__(cls):
		if cls.__instance is None:
			cls.__engine = create_engine(DATABASE_PATH)
			session = sessionmaker(bind=cls.__engine)
			cls.__instance = session()
		return cls.__instance

	@staticmethod
	def get_engine():
		return DatabaseConnection.__engine
