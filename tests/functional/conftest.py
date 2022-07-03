import asyncio
import pytest
import aiohttp
import redis

from dataclasses import dataclass

from elasticsearch import AsyncElasticsearch
from multidict import CIMultiDictProxy

from .settings import TestSettings

settings = TestSettings()


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


@pytest.fixture
def make_get_request(session):
    async def inner(method: str, params: dict = None) -> HTTPResponse:
        params = params or {}
        url = settings.base_api + method
        async with session.get(url, params=params) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )

    return inner


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def session(event_loop):
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture(scope="session")
def redis_client():
    return redis.Redis(
        settings.redis_host, settings.redis_port
    )  # type: ignore


@pytest.fixture(scope='session')
async def es_client():
    client = AsyncElasticsearch(hosts=f'{settings.es_host}:{settings.es_port}')
    yield client
    await client.close()
