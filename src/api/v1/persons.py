from http import HTTPStatus
from typing import List, Optional, Union, Tuple
from uuid import UUID

from fastapi.routing import APIRouter
from pydantic import BaseModel
from fastapi.param_functions import Depends, Query
from fastapi.exceptions import HTTPException
from fastapi_cache.decorator import cache

from services.persons import PersonService, get_person_service

router = APIRouter()


class Person(BaseModel):
    uuid: UUID
    full_name: str
    description: Union[str, None]


@router.get('/')
@cache(expire=60)
async def person_main(
        sort: Optional[str] = None,
        person_service: PersonService = Depends(get_person_service)
) -> List[Person]:
    """
    Main information of the person
    - **id**: person id
    - **full_name**: person full name

    """
    persons_all_fields = await person_service.get_all(sort=sort)
    return [Person(
        uuid=x.id, full_name=x.full_name
    ) for x in persons_all_fields]  # type: ignore


@router.get('/search/')
@cache(expire=60)
async def person_search(
        query: str,
        page_size: int = Query(50, alias="page[size]"),
        page_number: int = Query(1, alias="page[number]"),
        person_service: PersonService = Depends(
            get_person_service)) -> Tuple[Person, Optional[List[dict]]]:

    person = await person_service.person_search(query, page_size, page_number)

    return person  # type: ignore


@router.get('/{person_id}', response_model=Person)
@cache(expire=60)
async def person_details(
        person_id: str, person_service: PersonService = Depends(
            get_person_service)) -> Person:
    """
    Receive person details with this parameters
    - **id**: genre id
    - **name**: genre name

    """
    person = await person_service.get(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
    return Person(uuid=person.id, full_name=person.full_name)  # type: ignore
