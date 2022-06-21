from pydantic import UUID4

from pydantic import BaseModel

from models.base import BaseOrjsonModel


class GenreBase(BaseModel, BaseOrjsonModel.Config):
    id: UUID4
    name: str
