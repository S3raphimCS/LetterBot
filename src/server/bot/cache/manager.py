from typing import Dict

from server.bot.cache.store import cache_store


class RedisCacheManager:
    """Менеджер кэша в Redis."""

    store = cache_store

    @classmethod
    def set(cls, key: int, **kwargs) -> None:
        """Добавление записи в кеш."""
        key = str(key)
        data = cls.store.get(key=key)

        if data is None:
            return cls.store.add(key=key, data=kwargs)

        data.update(**kwargs)

        return cls.store.add(key=key, data=data)

    @classmethod
    def get(cls, key: int) -> Dict[str, str]:
        """Получение записи из кеша."""
        key = str(key)
        return cls.store.get(key=key)

    @classmethod
    def delete(cls, key: int) -> None:
        """Удаление записи из кеша."""
        key = str(key)
        cls.store.delete(key=key)
