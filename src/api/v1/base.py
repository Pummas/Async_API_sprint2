from typing import Optional

from pydantic import BaseModel, Field


class Request(BaseModel):
    sort: Optional[dict] = Field(title='Сортировка')
    query: Optional[dict] = Field(title='Запрос Эластика', default={"match_all": {}})
    page_size: Optional[int] = Field(title='Размер страницы', gt=1, default=25, alias='size')
    page_number: Optional[int] = Field(title='Страница поиска', gt=0, default=1, alias='from')