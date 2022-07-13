import json
import random
import uuid
import pytest
from ..conftest import settings
from ..testdata import es_indexes, films_bulk
from http import HTTPStatus

pytestmark = pytest.mark.asyncio


@pytest.fixture(scope="session")
async def setup_function(es_client):
    es_index = es_indexes.MovieIndex(settings.es_url, settings.es_port)
    await es_index.create_index('movies')
    data = ''
    for genre_index in films_bulk.data:
        for row in genre_index:
            data += f"{json.dumps(row)}\n"
    await es_client.bulk(data, 'movies', refresh=True)
    yield None
    await es_index.delete_index('movies')



async def test_get_all_films(setup_function, make_get_request):
    response = await make_get_request('/films')
    assert response.status == HTTPStatus.OK
    assert len(response.body) == 3


async def test_film(setup_function, make_get_request):
    random_elem = random.randint(0, len(films_bulk.data) - 1)
    data = films_bulk.data[random_elem]
    film_id = data[1].get('id')
    response = await make_get_request(
        f'/films/{film_id}/')
    assert response.status == HTTPStatus.OK
    assert response.body.get('uuid') == film_id
    assert response.body.get('title') == data[1].get('title')


async def test_search_film(setup_function, make_get_request):
    random_elem = random.randint(0, len(films_bulk.data) - 1)
    data = films_bulk.data[random_elem]
    film_id = data[1].get('id')
    title = data[1].get('title')
    response = await make_get_request(
        f'/films/search?query={title}&page%5Bsize%5D=25&page%5Bnumber%5D=1')
    assert response.status == HTTPStatus.OK
    assert response.body[0].get('uuid') == film_id
    assert response.body[0].get('title') == title


async def test_cache_film(setup_function, es_client,
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
    assert response_first.status == HTTPStatus.OK
    await es_client.delete('movies', uuid_key)
    response_second = await make_get_request(f'/films/{uuid_key}/')
    assert response_second.status == HTTPStatus.OK
    assert response_first.body == response_second.body
