from abc import ABC, abstractmethod


class DatabaseInterface(ABC):
    @abstractmethod
    def get_session(cls):
        pass

    @abstractmethod
    def get_engine(cls):
        pass
