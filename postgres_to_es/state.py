import abc
from typing import Any


class BaseStorage:
    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        """Сохранить состояние в постоянное хранилище"""
        pass

    @abc.abstractmethod
    def retrieve_state(self, name) -> dict:
        """Загрузить состояние локально из постоянного хранилища"""
        pass


# class JsonFileStorage(BaseStorage):
#     def __init__(self, file_path: Optional[str] = None):
#         self.file_path = file_path
#
#     def save_state(self, state: dict) -> None:
#         with open(self.file_path, "w") as file:
#             json.dump(state, file)
#
#     def retrieve_state(self) -> dict:
#         with open(self.file_path, "r") as file:
#             try:
#                 return json.load(file)
#             except Exception:
#                 return {}


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
        # self.storage.retrieve_state()

    def set_state(self, key: str, value: Any) -> None:
        """Установить состояние для определённого ключа"""
        self.storage.save_state({key: value})

    def get_state(self, state_name) -> Any:
        """Получить состояние по определённому ключу"""
        return self.storage.retrieve_state(state_name)
