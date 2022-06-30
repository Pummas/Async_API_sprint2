from pydantic import BaseModel
from uuid import UUID
from models.base import BaseOrjsonModel


class PersonBase(BaseModel, BaseOrjsonModel.Config):
    id: UUID
    name: str
