from typing import Type

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi.param_functions import Depends
from models.genre import GenreBase

from db.redis import RedisStorage
from db.elastic import ElasticSearch

from .base import Service


cache = RedisStorage()
elastic = ElasticSearch()


class GenreService(Service):
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        super(GenreService, self).__init__(redis=redis, elastic=elastic)

    @property
    def index(self) -> str:
        return 'genres'

    @property
    def model(self) -> Type[GenreBase]:
        return GenreBase


def get_genre_service(
        redis: RedisStorage = Depends(cache.get),
        elastic: ElasticSearch = Depends(elastic.get),
) -> GenreService:
    return GenreService(redis, elastic)  # type: ignore
