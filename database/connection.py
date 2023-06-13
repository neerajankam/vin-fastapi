from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.config import DATABASE_URL
from database.database_interface import DatabaseInterface


class Database(DatabaseInterface):
    """
    Singleton class for the database engine.

    Provides method to get a new session and access the engine.
    """

    __engine = None
    __session_factory = None

    @classmethod
    def get_session(cls):
        """
        Returns a new database session.

        :return: The database session.
        :rtype: SQLAlchemy session
        """
        if cls.__session_factory is None:
            cls.__session_factory = sessionmaker(bind=cls.get_engine())
        return cls.__session_factory()

    @classmethod
    def get_engine(cls):
        """
        Returns the database engine.

        :return: The database engine.
        :rtype: SQLAlchemy engine
        """
        if cls.__engine is None:
            cls.__engine = create_engine(DATABASE_URL)
        return cls.__engine
