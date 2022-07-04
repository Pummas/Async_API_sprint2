import json
import random
import uuid
from http import HTTPStatus

import pytest

from ..conftest import settings
from ..testdata import es_indexes, person_bulk

pytestmark = pytest.mark.asyncio


@pytest.fixture(scope="session")
async def setup_function(es_client):
    es_index = es_indexes.PersonIndex(settings.es_url, settings.es_port)
    await es_index.create_index('persons')
    data = ''
    for person_index in person_bulk.data:
        for row in person_index:
            data += f"{json.dumps(row)}\n"
    await es_client.bulk(data, 'persons', refresh=True)
    yield None
    await es_index.delete_index('persons')


async def test_get_all_persons(setup_function, make_get_request):
    response = await make_get_request('/persons')
    assert response.status == HTTPStatus.OK
    assert len(response.body) == 7


async def test_person(setup_function, make_get_request):
    random_elem = random.randint(0, len(person_bulk.data)-1)
    data = person_bulk.data[random_elem]
    person_id = data[1].get('id')
    response = await make_get_request(
        f'/persons/{person_id}/')
    assert response.status == HTTPStatus.OK
    assert response.body.get('uuid') == person_id
    assert response.body.get('full_name') == data[1].get('full_name')


async def test_search_person(setup_function, make_get_request):
    random_elem = random.randint(0, len(person_bulk.data)-1)
    data = person_bulk.data[random_elem]
    name = data[1].get('full_name')
    person_id = data[1].get('id')
    response = await make_get_request(
        f'/persons/search/?query={name}/')
    assert response.status == HTTPStatus.OK
    assert response.body[0].get('id') == person_id
    assert response.body[0].get('full_name') == name


async def test_cache_person(setup_function, es_client,
                            make_get_request, redis_client):
    uuid_key = uuid.uuid4()
    data = {"id": uuid_key, "full_name": "Test Testovich"}
    await es_client.create('persons', uuid_key, data)

    response_first = await make_get_request(f'/persons/{uuid_key}/')
    assert response_first.status == HTTPStatus.OK
    await es_client.delete('persons', uuid_key)
    response_second = await make_get_request(f'/persons/{uuid_key}/')
    assert response_second.status == HTTPStatus.OK
    assert response_first.body == response_second.body
