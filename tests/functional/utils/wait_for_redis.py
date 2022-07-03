import time
from functools import wraps

from redis import Redis

from ..settings import TestSettings

settings = TestSettings()
ES_PORT = settings.es_port

redis_host = settings.redis_host
redis_port = settings.redis_port


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


def wait_for_redis():
    r = Redis(host=redis_host,
              port=redis_port,
              socket_connect_timeout=1
              )  # short timeout for the tes
    try:
        return r.ping()
    except Exception as e:
        raise e
