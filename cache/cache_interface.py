from abc import ABC, abstractmethod


class CacheInterface(ABC):
    @abstractmethod
    def get(key):
        pass

    @abstractmethod
    def set(key, value):
        pass

    @abstractmethod
    def delete(key):
        pass
