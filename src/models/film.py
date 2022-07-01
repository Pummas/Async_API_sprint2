from typing import Optional, List
from pydantic import Field
from uuid import UUID
from models.base import BaseOrjsonModel
from models.person import PersonFilmwork


class FilmBase(BaseOrjsonModel):
    id: Optional[UUID]
    title: Optional[str]
    imdb_rating: Optional[float]
    description: Optional[str] = None
    genre: List[str]
    actors: List[PersonFilmwork]
    writers: Optional[List[PersonFilmwork]] = Field(default_factory=list)
    director: Optional[List[str]] = Field(default_factory=list)
