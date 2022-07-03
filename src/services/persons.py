from typing import Type

from aioredis import Redis
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch
from fastapi.param_functions import Depends
from models.person import OnlyPerson

from .base import Service


class PersonService(Service):
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        super(PersonService, self).__init__(redis=redis, elastic=elastic)

    @property
    def index(self) -> str:
        return 'persons'

    @property
    def model(self) -> Type[OnlyPerson]:
        return OnlyPerson

    async def person_search(self, query: str,
                            page_size: int, page_number: int
                            ):
        body = {
            'size': page_size,
            'from': (page_number - 1) * page_size,
            'query': {
                'simple_query_string': {
                    "query": query,
                    "fields": ["full_name"],
                    "default_operator": "or"
                }
            }
        }
        doc = await self.elastic.search(index='persons', body=body, size=10000)
        persons = [OnlyPerson(**x['_source']) for x in doc['hits']['hits']]
        return persons


def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
