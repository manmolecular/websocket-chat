#!/usr/bin/env python3

from redis import Redis

from chat.utils.config import CacheValues


class RedisCache:
    def __init__(
        self,
        host: str = CacheValues.REDIS_HOST,
        expire: int = CacheValues.REDIS_EXP,
    ):
        self.options = dict(expire=expire)
        self.redis = Redis(host=host)

    def get(self, key) -> dict or list:
        if self.exists(key):
            return self.redis.get(key)
        return None

    def set(self, key, value, expire=None) -> None:
        self.redis.set(key, value)
        if expire:
            self.redis.expire(key, expire)
        else:
            self.redis.expire(key, self.options["expire"])

    def delitem(self, key) -> None:
        self.redis.delete(key)

    def exists(self, key) -> bool:
        return bool(self.redis.exists(key))
