from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from database.connection import DatabaseConnection


Base = declarative_base()
db_session = DatabaseConnection()


class Vin(Base):
    """
    Represents the VIN table in the database.
    """

    __tablename__ = "vins"

    vin = Column(String(17), primary_key=True)
    vehicle_details = Column(Text(255))


# Create the tables
Base.metadata.create_all(bind=DatabaseConnection.get_engine())
