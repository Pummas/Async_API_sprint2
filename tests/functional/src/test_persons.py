import uuid

import pytest

from ..conftest import settings
from ..testdata import es_indexes, persons_bulk


@pytest.fixture(scope="session")
async def setup_function(es_client):
    es_index = es_indexes.PersonIndex(settings.es_url, settings.es_port)
    await es_index.create_index('persons')
    await es_client.bulk(persons_bulk.data, 'persons', refresh=True)
    yield None
    await es_index.delete_index('persons')


@pytest.mark.asyncio
async def test_get_all_persons(setup_function, make_get_request):
    response = await make_get_request('/persons')
    assert response.status == 200
    assert len(response.body) == 29


@pytest.mark.asyncio
async def test_person(setup_function, make_get_request):
    response = await make_get_request(
        '/persons/fc24f8c1-6bf0-468e-a3a8-2750e5f7abe5/')
    assert response.status == 200
    assert response.body.get('uuid') == 'fc24f8c1-6bf0-468e-a3a8-2750e5f7abe5'
    assert response.body.get('full_name') == 'Gary Goddard'


@pytest.mark.asyncio
async def test_search_person(setup_function, make_get_request):
    response = await make_get_request(
        '/persons/search/?query=Gary Goddard/')
    assert response.status == 200
    assert response.body[0].get('id') == 'fc24f8c1-6bf0-468e-a3a8-2750e5f7abe5'
    assert response.body[0].get('full_name') == 'Gary Goddard'


@pytest.mark.asyncio
async def test_cache_person(setup_function, es_client,
                            make_get_request, redis_client):
    uuid_key = uuid.uuid4()
    data = {"id": uuid_key, "full_name": "Test Testovich"}
    await es_client.create('persons', uuid_key, data)

    response_first = await make_get_request(f'/persons/{uuid_key}/')
    assert response_first.status == 200
    await es_client.delete('persons', uuid_key)
    response_second = await make_get_request(f'/persons/{uuid_key}/')
    assert response_second.status == 200
    assert response_first.body == response_second.body
