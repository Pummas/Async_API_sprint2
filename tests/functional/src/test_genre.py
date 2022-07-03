import uuid
import pytest
from ..conftest import settings
from ..testdata import es_indexes, genres_bulk


@pytest.fixture(scope="session")
async def setup_function(es_client):
    es_index = es_indexes.GenresIndex(settings.es_url, settings.es_port)
    await es_index.create_index('genres')
    await es_client.bulk(genres_bulk.data, 'genres', refresh=True)
    yield None
    await es_index.delete_index('genres')


@pytest.mark.asyncio
async def test_get_all_genres(setup_function, make_get_request):
    response = await make_get_request('/genres')
    assert response.status == 200
    assert len(response.body) == 26


@pytest.mark.asyncio
async def test_genre(setup_function, make_get_request):
    response = await make_get_request(
        '/genres/f24fd632-b1a5-4273-a835-0119bd12f829/')
    assert response.status == 200
    assert response.body.get('uuid') == 'f24fd632-b1a5-4273-a835-0119bd12f829'
    assert response.body.get('name') == 'News'


@pytest.mark.asyncio
async def test_cache_genre(setup_function, es_client,
                           make_get_request, redis_client):
    uuid_key = uuid.uuid4()
    data = {"id": uuid_key, "name": "Test"}
    await es_client.create('genres', uuid_key, data)

    response_first = await make_get_request(f'/genres/{uuid_key}/')
    assert response_first.status == 200
    await es_client.delete('genres', uuid_key)
    response_second = await make_get_request(f'/genres/{uuid_key}/')
    assert response_second.status == 200
    assert response_first.body == response_second.body
