from http import HTTPStatus
from typing import List, Optional, Union
from uuid import UUID

from fastapi.routing import APIRouter
from pydantic import BaseModel
from fastapi.param_functions import Depends
from fastapi.exceptions import HTTPException
from fastapi_cache.decorator import cache

from services.genre import GenreService, get_genre_service
from .base import Request


router = APIRouter()

class Genre(BaseModel):
    uuid: UUID
    name: str
    description: Union[str, None]


@router.get('/')
@cache(expire=60)
async def genre_main(
        sort: Optional[str] = None,
        genre_service: GenreService = Depends(get_genre_service)
) -> List[Genre]:
    """
    Main information of the genre
    
    - **id**: genre id
    - **name**: genre name 
    """
    genres = await genre_service.get_all(sort=sort)
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
    return [Genre(uuid=x.id, name=x.name, description=x.description) for x in genres]


@router.post('/search/')
@cache(expire=60)
async def genre_search(
        search: Request,
        genre_service: GenreService = Depends(get_genre_service)
) -> List[Genre]:
    """
    Genre search
    
    - **id**: genre id
    - **name**: genre name 
    """
    genres = await genre_service.search(body=search.dict(by_alias=True))
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
    return [Genre(uuid=x.id, name=x.name) for x in genres]  # type: ignore


@router.get('/{genre_id}', response_model=Genre)
@cache(expire=60)
async def genre_details(genre_id: str, genre_service: GenreService = Depends(get_genre_service)) -> Genre:
    """
    Receive genre details with this parameters
    
    - **id**: genre id
    - **name**: genre name 
    """
    genre = await genre_service.get(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
    return Genre(uuid=genre.id, name=genre.name)  # type: ignore
