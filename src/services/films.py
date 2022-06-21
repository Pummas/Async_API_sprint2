from typing import Type

from aioredis import Redis
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch
from fastapi.param_functions import Depends
from models.film import FilmBase

from .base import Service


class FilmService(Service):
    @property
    def index(self) -> str:
        return 'movies'

    @property
    def model(self) -> Type[FilmBase]:
        return FilmBase

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        super(FilmService, self).__init__(redis=redis, elastic=elastic)


def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
