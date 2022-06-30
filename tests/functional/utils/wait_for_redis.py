import os
from dotenv import load_dotenv
from redis import Redis
from time import sleep

load_dotenv()

redis_host = os.environ.get('REDIS_HOST', 'localhost')
redis_port = os.environ.get('REDIS_PORT', '6379')


def wait_for_redis():
    r = Redis(host=redis_host, port=redis_port, socket_connect_timeout=1)  # short timeout for the test
    for i in range(10):
        try:
            return r.ping()
        except Exception as e:
            print(e)
            sleep(1)
    return False


