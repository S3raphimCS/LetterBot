import json
from typing import Dict

from django.conf import settings
import redis


redis = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    encoding='utf-8',
    decode_responses=True,
)


class RedisStorage:
    """Класс хранилища кэша в Redis."""

    @classmethod
    def add(cls, key: str, data: Dict[str, str]) -> None:
        """Метод добавления записи в кеш."""
        redis.set(
            name=key,
            value=json.dumps(data),
        )

    @classmethod
    def get(cls, key: str) -> Dict[str, str]:
        """Метод получения записи из кэша."""
        result = redis.get(key)
        return json.loads(result) if result else {}

    @classmethod
    def delete(cls, key: str) -> None:
        """Метод удаления записи из кеша."""
        redis.delete(key)


cache_store = RedisStorage()
