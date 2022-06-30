from pydantic import BaseModel
from uuid import UUID
from models.base import BaseOrjsonModel


class PesBase(BaseModel, BaseOrjsonModel.Config):
    id: UUID
    name: str