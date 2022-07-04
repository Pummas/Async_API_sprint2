from abc import ABC, abstractmethod
from typing import Optional
from aioredis import Redis


class AsyncCacheStorage(ABC):
    @abstractmethod
    async def get(self, key: str, **kwargs):
        pass

    @abstractmethod
    async def set(self, key: str, value: str, expire: int, **kwargs):
        pass


redis: Optional[Redis] = None


class RedisStorage(AsyncCacheStorage):
    async def get(self) -> Redis:
        return redis

    async def set(self, key: str, value: str, expire: int, **kwargs):
        pass
