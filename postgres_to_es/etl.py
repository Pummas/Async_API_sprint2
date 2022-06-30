import abc
import json
import time
from functools import wraps
from logging import getLogger
import requests

from postgres_loader import PostgresLoader
from state import State


def backoff(logger, start_sleep_time=0.1, factor=2, border_sleep_time=10):
    """
    Функция для повторного выполнения функции
    через некоторое время, если возникла ошибка.
    Использует наивный экспоненциальный рост времени повтора (factor)
    до граничного времени ожидания (border_sleep_time)
    """

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            n = 1
            sleep_time = start_sleep_time * factor ** n
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.error(e)
                    if sleep_time < border_sleep_time:
                        time.sleep(sleep_time)
                        n += 1
                        sleep_time = start_sleep_time * factor ** n
                    else:
                        time.sleep(border_sleep_time)

        return inner

    return func_wrapper


class ETLExtract:
    @abc.abstractmethod
    def extract(self, pg_table: PostgresLoader, state_name: str) -> tuple:
        pass


class ETLTransform:
    def transform(self, data: dict, index_name: str) -> str:
        """Преобразовать данные в нужный формат"""
        request = json.dumps(
            {"index": {"_index": index_name, "_id": data["id"]}}
        )
        return f"{request}\n {json.dumps(data)} \n"


class ETLLoad:
    @abc.abstractmethod
    def loader(self, data: list, url: str,
               port: int, state: str, index_name: str):
        pass


class ETLProcess(ETLExtract, ETLTransform, ETLLoad):
    """
    Класс для переноса данных из PostgreSQL в Elasticsearch
    """

    def __init__(self, state: State):
        self.states = state
        self.state = ''

    # @backoff(logger=getLogger())
    def extract(self, pg_table: PostgresLoader, state_name: str) -> tuple:
        """Взять состояние и учитывая состояние
        получить данные из PostgreSQL"""
        try:
            self.state = self.states.get_state(state_name)
            data = pg_table.load(self.state)
            if len(data) == 0:
                return data, self.state
            data_to_transform, state = pg_table.load_data(data)
            return data_to_transform, state
        except Exception as e:
            raise e

    # @backoff(logger=getLogger())
    def loader(self, data: list, url: str,
               port: int, state: str, index_name: str):
        """Загрузить данные в Elasticsearch и обновить состояние"""
        try:
            transform_data = ''
            for elem in data:
                transform_elem = self.transform(elem, index_name)
                transform_data += transform_elem
            bulk_url = f'{url}:{port}/_bulk'
            requests.post(
                bulk_url,
                data=transform_data,
                headers={
                    'content-type': 'application/json', 'charset': 'UTF-8'
                }
            )
            self.states.set_state(index_name, state)
        except Exception as e:
            raise e
