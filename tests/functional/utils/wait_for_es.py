import time
from functools import wraps

from elasticsearch import Elasticsearch

from ..settings import TestSettings

settings = TestSettings()
ES_HOST = settings.es_host
ES_PORT = settings.es_port


def backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10):
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
                except Exception:
                    if sleep_time < border_sleep_time:
                        time.sleep(sleep_time)
                        n += 1
                        sleep_time = start_sleep_time * factor ** n
                    else:
                        time.sleep(border_sleep_time)

        return inner

    return func_wrapper


@backoff
def wait_for_es():
    es = Elasticsearch([f'http://{ES_HOST}:{ES_PORT}'], verify_certs=True)
    ping = es.ping()
    if ping:
        return ping
    raise Exception
