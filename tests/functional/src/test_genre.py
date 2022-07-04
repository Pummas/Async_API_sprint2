import json
import random
import uuid
from http import HTTPStatus

import pytest
from ..conftest import settings
from ..testdata import es_indexes, genres_bulk

pytestmark = pytest.mark.asyncio


@pytest.fixture(scope="session")
async def setup_function(es_client):
    es_index = es_indexes.GenresIndex(settings.es_url, settings.es_port)
    await es_index.create_index('genres')
    data = ''
    for genre_index in genres_bulk.data:
        for row in genre_index:
            data += f"{json.dumps(row)}\n"
    await es_client.bulk(data, 'genres', refresh=True)
    yield None
    await es_index.delete_index('genres')


async def test_get_all_genres(setup_function, make_get_request):
    response = await make_get_request('/genres')
    assert response.status == HTTPStatus.OK
    assert len(response.body) == 13


async def test_genre(setup_function, make_get_request):
    random_elem = random.randint(0, len(genres_bulk.data)-1)
    data = genres_bulk.data[random_elem]
    genre_id = data[1].get('id')
    response = await make_get_request(
        f'/genres/{genre_id}/')
    assert response.status == HTTPStatus.OK
    assert response.body.get('uuid') == genre_id
    assert response.body.get('name') == data[1].get('name')


async def test_cache_genre(setup_function, es_client,
                           make_get_request, redis_client):
    uuid_key = uuid.uuid4()
    data = {"id": uuid_key, "name": "Test"}
    await es_client.create('genres', uuid_key, data)

    response_first = await make_get_request(f'/genres/{uuid_key}/')
    assert response_first.status == HTTPStatus.OK
    await es_client.delete('genres', uuid_key)
    response_second = await make_get_request(f'/genres/{uuid_key}/')
    assert response_second.status == HTTPStatus.OK
    assert response_first.body == response_second.body
