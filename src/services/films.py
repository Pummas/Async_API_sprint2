from typing import Type, Dict, List

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

    async def search_films(self, body: Dict):
        doc = await self.elastic.search(index='movies', body=body)
        list_films = [FilmBase(**x['_source']) for x in doc['hits']['hits']]
        return list_films

    async def get_film_search(self, query: str, page_size: int,
                              page_number: int) -> List[FilmBase]:
        body = {
            'size': page_size,
            'from': (page_number - 1) * page_size,
            'query': {
                'simple_query_string': {
                    "query": query,
                    "fields": ["title^3", "description"],
                    "default_operator": "or"
                }
            }
        }
        doc = await self.search_films(body)
        return doc


def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
