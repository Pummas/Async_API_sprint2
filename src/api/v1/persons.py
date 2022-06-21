import code
from http import HTTPStatus
from typing import List, Optional, Union
from uuid import UUID

from fastapi.routing import APIRouter
from pydantic import BaseModel
from fastapi.param_functions import Depends
from fastapi.exceptions import HTTPException
from fastapi_cache.decorator import cache

from services.persons import PersonService, get_person_service
from .base import Request


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
    return [Person(uuid=x.id, full_name=x.full_name) for x in persons_all_fields]  # type: ignore


@router.post('/search/')
@cache(expire=60)
async def person_search(
        search: Request,
        person_service: PersonService = Depends(get_person_service)) -> List[Person]:
    """
    Person search
    
    - **id**: person id
    - **full_name**: person full name 
    """
    persons_all_fields_search = await person_service.search(body=search.dict(by_alias=True))
    return [Person(uuid=x.id, full_name=x.full_name) for x in persons_all_fields_search]  # type: ignore


@router.get('/{person_id}', response_model=Person)
@cache(expire=60)
async def person_details(person_id: str, person_service: PersonService = Depends(get_person_service)) -> Person:
    """
    Receive person details with this parameters
    
    - **id**: genre id
    - **name**: genre name 
    """
    person = await person_service.get(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
    return Person(uuid=person.id, full_name=person.full_name)  # type: ignore
