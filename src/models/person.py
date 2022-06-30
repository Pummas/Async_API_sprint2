from pydantic import BaseModel
from uuid import UUID
from models.base import BaseOrjsonModel


class PersonBase(BaseModel, BaseOrjsonModel.Config):
    id: UUID


class PersonFilmwork(PersonBase):
    name: str


class OnlyPerson(PersonBase):
    full_name: str
