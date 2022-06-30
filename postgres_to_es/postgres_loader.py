import os
from logging import getLogger
from typing import List, Tuple
from abc import abstractmethod

import psycopg2
from dotenv import load_dotenv

load_dotenv()


class LoadData:
    @abstractmethod
    def load_data(self, data: list) -> Tuple[list, str]:
        pass


class Load:
    @abstractmethod
    def load(self, state: str) -> list:
        pass


class PostgresLoader(LoadData, Load):
    """
    Класс, реализующий запросы к PostgreSQL
    """

    def __init__(self, pg_conn: psycopg2.extensions.connection):
        self._connection = pg_conn
        self._cursor = self._connection.cursor()
        self._logger = getLogger()

    def load_data(self, data: list) -> Tuple[list, str]:
        """Выдать ограниченное число фильмов, жанров и актеров
        отсортированных по дате изменения фильмов"""
        try:
            films_id, state = self.get_films_id(data)
            self._cursor.execute(get_films_sql_request.format(films_id))
            return self._cursor.fetchall(), state
        except Exception as e:
            self._logger.error(e)

    def get_films_id(self, data: list) -> Tuple[str, str]:
        """Получить id фильмов"""
        try:
            films_id = []
            for elem in data:
                films_id.append(elem.get('id'))
            return str(films_id)[1:-1], data[-1].get('modified')
        except Exception as e:
            self._logger.error(e)

    def load(self, state: str) -> list:
        pass


class PostgresFilmGenre(PostgresLoader):
    def load(self, state: str) -> list:
        """Вывести таблицу с id фильмов и modified"""
        try:
            self._cursor.execute(
                f"""
                SELECT
                    film_work_id as id,
                    to_char(genre.modified, 'YYYY-MM-DD HH24:MI:SS.US')
                    as modified
                FROM content.genre
                JOIN  content.genre_film_work gfw on genre.id = gfw.genre_id
                WHERE modified > '{state}'
                LIMIT {os.environ.get('BATCH_SIZE')};
                """)  # noqa: S608
            return self._cursor.fetchall()
        except Exception as e:
            self._logger.error(e)


class PostgresFilmPerson(PostgresLoader):
    def load(self, state: str) -> list:
        """Вывести таблицу с id фильмов и modified"""
        try:
            self._cursor.execute(
                f"""
                SELECT
                    film_work_id as id,
                    to_char(person.modified, 'YYYY-MM-DD HH24:MI:SS.US')
                    as modified
                FROM content.person
                JOIN content.person_film_work pfw on person.id = pfw.person_id
                WHERE modified > '{state}'
                LIMIT {os.environ.get('BATCH_SIZE')};
                """)  # noqa: S608
            return self._cursor.fetchall()
        except Exception as e:
            self._logger.error(e)


class PostgresFilmWork(PostgresLoader):
    def load(self, state: str) -> list:
        """Вывести таблицу с id фильмов и modified"""
        try:
            self._cursor.execute(
                f"""
                SELECT
                    id,
                    to_char(modified, 'YYYY-MM-DD HH24:MI:SS.US')
                    as modified
                FROM content.film_work
                WHERE modified > '{state}'
                LIMIT {os.environ.get('BATCH_SIZE')};
                """)  # noqa: S608
            return self._cursor.fetchall()
        except Exception as e:
            self._logger.error(e)


class PostgresTransformData(PostgresLoader):
    """Класс, для возможности использовать
    базовый класс и не ломать старую логику"""

    def load_data(self, data: List[dict]) -> Tuple[list, str]:
        """Убрать из данных поле modified и
        выдать последний из них вместе с датой"""
        state = ''
        for row in data:
            state = row.pop('modified')
        return data, state


class PostgresPerson(PostgresTransformData):
    def load(self, state: str) -> list:
        """Выдать всех людей, участвующих в любых фильмах"""
        try:
            self._cursor.execute(
                f"""
                SELECT DISTINCT person.id, full_name as full_name,
                to_char(modified, 'YYYY-MM-DD HH24:MI:SS.US')
                    as modified
                FROM content.person
                JOIN content.person_film_work pfw on person.id = pfw.person_id
                WHERE modified > '{state}'
                ORDER BY modified
                LIMIT {os.environ.get('BATCH_SIZE')};
                """)  # noqa: S608
            return self._cursor.fetchall()
        except Exception as e:
            self._logger.error(e)


class PostgresGenre(PostgresTransformData):
    def load(self, state: str) -> list:
        """Выдать все жанры, присутствующих в любых фильмах"""
        try:
            self._cursor.execute(
                f"""
                SELECT DISTINCT genre.id, name,
                to_char(modified, 'YYYY-MM-DD HH24:MI:SS.US')
                    as modified
                FROM content.genre
                JOIN content.genre_film_work gfw on genre.id = gfw.genre_id
                WHERE modified > '{state}'
                ORDER BY modified
                LIMIT {os.environ.get('BATCH_SIZE')};
                """)  # noqa: S608
            return self._cursor.fetchall()
        except Exception as e:
            self._logger.error(e)


get_films_sql_request = """
SELECT fw.id,
fw.rating as imdb_rating,
array_agg(DISTINCT g.name) as genre,
fw.title,
fw.description,
array_remove(array_agg(DISTINCT p.full_name)
    FILTER ( WHERE role = 'director' ), null) as director,
array_remove(array_agg(DISTINCT p.full_name)
    FILTER ( WHERE role = 'actor' ),  null)   as actors_names,
array_remove(array_agg(DISTINCT p.full_name)
    FILTER ( WHERE role = 'writer' ), null)  as writers_names,
  COALESCE(
           json_agg(
           DISTINCT jsonb_build_object(
                   'id', p.id,
                   'name', p.full_name
               )
       ) FILTER (WHERE p.id is not null),
           '[]'
)                                            as actors,
COALESCE(
           json_agg(
           DISTINCT jsonb_build_object(
                   'id', p.id,
                   'name', p.full_name
               )
       ) FILTER (WHERE p.id is not null and role = 'writer'),
           '[]'
)                                            as writers
FROM content.film_work fw
LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
LEFT JOIN content.person p ON p.id = pfw.person_id
LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
LEFT JOIN content.genre g ON g.id = gfw.genre_id
WHERE fw.id IN ({0})
GROUP BY fw.id
"""
