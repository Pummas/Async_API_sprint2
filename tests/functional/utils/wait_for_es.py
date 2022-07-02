import os
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from time import sleep

load_dotenv()

ES_HOST = os.environ.get('ELASTIC_HOST', '127.0.0.1')
ES_PORT = os.environ.get('ELASTIC_PORT', 9200)


def wait_for_es():
    es = Elasticsearch([f'http://{ES_HOST}:{ES_PORT}'], verify_certs=True)
    ping = es.ping()
    for i in range(10):
        if ping:
            return ping
        ping = es.ping()
        sleep(1)
    return ping
