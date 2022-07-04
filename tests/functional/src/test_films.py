import uuid
import pytest
from ..conftest import settings
from ..testdata import es_indexes, films_bulk


@pytest.fixture(scope="session")
async def setup_function(es_client):
    es_index = es_indexes.MovieIndex(settings.es_url, settings.es_port)
    await es_index.create_index('movies')
    await es_client.bulk(films_bulk.data, 'movies', refresh=True)
    yield None
    await es_index.delete_index('movies')


@pytest.mark.asyncio
async def test_get_all_films(setup_function, make_get_request):
    response = await make_get_request('/films')
    assert response.status == 200
    assert len(response.body) == 3


@pytest.mark.asyncio
async def test_film(setup_function, make_get_request):
    response = await make_get_request(
        '/films/f06315d4-eab6-4fdc-b768-7c046cedfd9b/')
    assert response.status == 200
    assert response.body.get('uuid') == 'f06315d4-eab6-4fdc-b768-7c046cedfd9b'
    title = 'Starmania. \u00d6sterreich sucht den neuen Star'
    assert response.body.get('title') == title


@pytest.mark.asyncio
async def test_search_film(setup_function, make_get_request):
    response = await make_get_request(
        '/films/search?query=Star&page%5Bsize%5D=25&page%5Bnumber%5D=1')
    assert response.status == 200
    uuid = 'fe12e428-be67-4bb9-9629-4ab1385dc8be'
    assert response.body[0].get('uuid') == uuid
    assert response.body[0].get('title') == 'Crescent Star'


@pytest.mark.asyncio
async def test_cache_genre(setup_function, es_client,
                           make_get_request, redis_client):
    uuid_key = uuid.uuid4()
    data = {
        "id": uuid_key, "imdb_rating": 8.7,
        "title": "TestFilm", "description": None,
        "director": None, "actors_names": ["Arabella Kiesbauer"],
        "writers_names": ["Mischa Zickler"],
        "genre": ["Drama", "Short"],
        "actors": [{"id": "50596339-355b-4abb-9955-645f3e3ecf34",
                    "name": "Arabella Kiesbauer"}]}
    await es_client.create('movies', uuid_key, data)

    response_first = await make_get_request(f'/films/{uuid_key}/')
    assert response_first.status == 200
    await es_client.delete('movies', uuid_key)
    response_second = await make_get_request(f'/films/{uuid_key}/')
    assert response_second.status == 200
    assert response_first.body == response_second.body
