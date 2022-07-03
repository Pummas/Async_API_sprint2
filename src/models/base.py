from uuid import UUID, uuid4

from pydantic import BaseModel as PydanticBaseModel, Field
import orjson


def orjson_dumps(v, *, default) -> str:
    return orjson.dumps(v, default=default).decode()


class BaseModel(PydanticBaseModel):
    id: UUID = Field(default_factory=uuid4)

    class Config:
        arbitrary_types_allowed = True
        json_loads = orjson.loads
        json_dumps = orjson.dumps


class BaseOrjsonModel(BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
