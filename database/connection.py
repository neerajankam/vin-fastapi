import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


HERE = os.path.dirname(os.path.abspath(__file__))
DATABASE_NAME = "vins_database.db"
DATABASE_PATH = os.path.join(HERE, "..", "data")
DATABASE_URL = f"sqlite:///{DATABASE_PATH}/{DATABASE_NAME}"


class DatabaseConnection:
    """
    Singleton class for managing the database connection.

    Provides methods to get the database engine and a session object.
    """

    __instance = None
    __engine = None

    def __new__(cls) -> "DatabaseConnection":
        """
        Creates a new instance of the DatabaseConnection class.

        :return: The DatabaseConnection instance.
        :rtype: DatabaseConnection
        """
        if cls.__instance is None:
            cls.__engine = create_engine(DATABASE_URL)
            session = sessionmaker(bind=cls.__engine)
            cls.__instance = session()
        return cls.__instance

    @classmethod
    def get_engine(cls) -> "Engine":
        """
        Retrieves the database engine.

        :return: The database engine.
        :rtype: Engine
        """
        return cls.__engine
