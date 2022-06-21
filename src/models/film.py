from typing import Optional, List
from pydantic import Field
from uuid import UUID
from models.base import BaseOrjsonModel
from models.genre import GenreBase
from models.person import PersonBase


class FilmBase(BaseOrjsonModel):
    id: Optional[UUID]
    title: Optional[str]
    imdb_rating: Optional[float]
    description: Optional[str] = None
    genre: List[GenreBase]
    actors: List[PersonBase]
    writers: Optional[List[PersonBase]] = Field(default_factory=list)
    directors: Optional[List[PersonBase]] = Field(default_factory=list)

