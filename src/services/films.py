from typing import Type, Dict, List

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi.param_functions import Depends

from models.film import FilmBase
from db.redis import RedisStorage
from db.elastic import ElasticSearch

from .base import Service

cache = RedisStorage()
elastic = ElasticSearch()


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
        redis: RedisStorage = Depends(cache.get),
        elastic: ElasticSearch = Depends(elastic.get),
) -> FilmService:
    return FilmService(redis, elastic)  # type: ignore
