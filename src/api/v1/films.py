from http import HTTPStatus
from typing import List, Optional, Union
from uuid import UUID

from fastapi.routing import APIRouter
from pydantic import BaseModel
from fastapi.param_functions import Depends, Query
from fastapi.exceptions import HTTPException
from fastapi_cache.decorator import cache

from services.films import FilmService, get_film_service


router = APIRouter()


class FilmMain(BaseModel):
    uuid: Optional[UUID]
    title: Optional[str]
    imdb_rating: Optional[float]
    description: Union[str, None]


class FilmDetail(FilmMain):
    description: Optional[str]
    genre: Optional[List[str]]
    actors: Optional[List[dict]]
    writers: Optional[List[dict]]
    director: Optional[List[str]]


@router.get('/')
@cache(expire=60)
async def film_main(
        sort: Optional[str] = "-imdb_rating",
        film_service: FilmService = Depends(get_film_service)
) -> List[FilmMain]:
    """
    Main information of the film
    - **id**: film id
    - **title**: film title
    - **imdb_rating**: imdb rating of film

    """
    films_all_fields = await film_service.get_all(sort=sort)
    return [FilmMain(
        uuid=x.id, title=x.title,
        imdb_rating=x.imdb_rating, description=x.description
    ) for x in films_all_fields]


@router.get('/search')
async def film_search(
        query: str,
        page_size: int = Query(25, alias="page[size]"),
        page_number: int = Query(1, alias="page[number]"),
        film_service:
        FilmService = Depends(get_film_service)) -> List[FilmMain]:
    films_all_fields_search = await film_service.get_film_search(query,
                                                                 page_size,
                                                                 page_number)
    films = [FilmMain(
        uuid=x.id, title=x.title,
        imdb_rating=x.imdb_rating
        ) for x in films_all_fields_search]
    return films


@router.get('/{film_id}', response_model=FilmDetail)
@cache(expire=60)
async def film_details(
        film_id: str,
        film_service: FilmService = Depends(
            get_film_service)) -> FilmDetail:
    """
    Receive film details with this parameters
    - **id**: film id
    - **title**: film title
    - **description**: description of film
    - **imdb_rating**: imdb rating of film
    - **genre**: genre of film
    - **actors**: actors which are participated in the film
    - **writers**: writers of the film
    - **director**: director of the film

    """
    film = await film_service.get(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

    return FilmDetail(
        uuid=film.id,
        title=film.title,
        imdb_rating=film.imdb_rating,
        description=film.description,
        # type: ignore
        genre=film.genre,
        actors=film.actors,
        writers=film.writers,
        director=film.director
    )  # type: ignore
