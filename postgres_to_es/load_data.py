import os
import time
import logging
import psycopg2.extras
from dotenv import load_dotenv
from redis import Redis
from etl import ETLProcess
from state import State, RedisStorage
from postgres_loader import PostgresFilmGenre, PostgresFilmPerson, \
    PostgresFilmWork, PostgresLoader, PostgresPerson, PostgresGenre
from es_indexes import MovieIndex, PersonIndex, GenresIndex

load_dotenv()


def create_indexes(url, port):
    """Создать индекс, если его нет"""
    indexes_names = {
        MovieIndex: 'movies',
        PersonIndex: 'persons',
        GenresIndex: 'genres'
    }
    for index, name in indexes_names.items():
        create_index = index(url, port)
        create_index.create_index(name)


def load_data(url: str, port: int,
              postgres_table: PostgresLoader, index_name: str) -> None:
    """Основная функция переноса всех данных из PostgreSQL в Elasticsearch"""
    while True:
        data, state = etl.extract(postgres_table, index_name)
        if len(data) == 0:
            return
        etl.loader(data, url, port, state, index_name)


if __name__ == '__main__':
    logger = logging.getLogger()
    logging.basicConfig(level=logging.INFO)

    dsl = {
        'dbname': os.environ.get('DB_NAME'),
        'user': os.environ.get('DB_USER'),
        'password': os.environ.get('DB_PASSWORD'),
        'host': os.environ.get('DB_HOST'),
        'port': os.environ.get('DB_PORT')
    }

    elastic_host = os.environ.get('ELASTIC_HOST', 'localhost')
    elastic_url = f'http://{elastic_host}'
    elastic_port = os.environ.get('ELASTIC_PORT', 9200)

    time_sleep = int(os.environ.get('TIME_SLEEP', 100))

    redis_host = os.environ.get('REDIS_HOST', 'localhost')
    redis_port = os.environ.get('REDIS_PORT', '6379')
    file_storage = RedisStorage(Redis(
        host=redis_host, port=redis_port, db=0))
    tables = {
        PostgresFilmWork: 'movies',
        PostgresFilmGenre: 'movies',
        PostgresFilmPerson: 'movies',
        PostgresPerson: 'persons',
        PostgresGenre: 'genres'
    }
    states = State(storage=file_storage)
    create_indexes(elastic_url, elastic_port)
    # if states.get_state('movies') is None:
    states.set_state('movies', '1000-04-10')
    states.set_state('persons', '1000-04-10')
    states.set_state('genres', '1000-04-10')
    while True:
        with psycopg2.connect(
                **dsl, cursor_factory=psycopg2.extras.RealDictCursor
        ) as pg_conn:
            etl = ETLProcess(states)
            for key, value in tables.items():
                load_data(elastic_url, elastic_port, key(pg_conn), value)
                logger.info(f'successful {str(key)} transfer')
        logger.info('successful transfer of all tables')
        pg_conn.close()
        time.sleep(time_sleep)
