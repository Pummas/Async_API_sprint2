import abc
from typing import Any


class SaveStateStorage:
    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        """Сохранить состояние в постоянное хранилище"""
        pass


class RetrieveStateStorage:
    @abc.abstractmethod
    def retrieve_state(self, name) -> dict:
        """Загрузить состояние локально из постоянного хранилища"""
        pass


class BaseStorage(SaveStateStorage, RetrieveStateStorage):
    def save_state(self, state: dict) -> None:
        """Сохранить состояние в постоянное хранилище"""
        pass

    def retrieve_state(self, name) -> dict:
        """Загрузить состояние локально из постоянного хранилища"""
        pass


class RedisStorage(BaseStorage):
    def __init__(self, redis_adapter):
        self.redis = redis_adapter

    def save_state(self, state: dict) -> None:
        for key, value in state.items():
            self.redis.set(key, value)

    def retrieve_state(self, name) -> dict:
        data = self.redis.get(name)
        if data is None:
            return {}
        return data.decode("utf-8")


class State:
    """
    Класс для хранения состояния при работе с данными,
    чтобы постоянно не перечитывать данные с начала.
    """

    def __init__(self, storage: BaseStorage):
        self.storage = storage

    def set_state(self, key: str, value: Any) -> None:
        """Установить состояние для определённого ключа"""
        self.storage.save_state({key: value})

    def get_state(self, state_name) -> Any:
        """Получить состояние по определённому ключу"""
        return self.storage.retrieve_state(state_name)
