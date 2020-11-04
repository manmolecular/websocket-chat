#!/usr/bin/env python3

from redis import Redis

from chat.utils.config import CacheValues


class RedisCache:
    """
    Redis cache handler
    """
    def __init__(
        self, host: str = CacheValues.REDIS_HOST, expire: int = CacheValues.REDIS_EXP,
    ):
        """
        Init handler with host to connect and default expiration time in seconds
        :param host: host to connect
        :param expire: expiration time
        """
        self.options = dict(expire=expire)
        self.redis = Redis(host=host)

    def get(self, key) -> dict or list or None:
        """
        Get value by key
        :param key: key
        :return: value
        """
        if self.exists(key):
            return self.redis.get(key)
        return None

    def set(self, key, value, expire=None) -> None:
        """
        Set value by key
        :param key: key
        :param value: value
        :param expire: expiration time in seconds, or default from self
        :return: None
        """
        self.redis.set(key, value)
        if expire:
            self.redis.expire(key, expire)
        else:
            self.redis.expire(key, self.options["expire"])

    def delitem(self, key) -> None:
        """
        Delete value by key
        :param key: key to use
        :return: None
        """
        self.redis.delete(key)

    def exists(self, key) -> bool:
        """
        Check if key exists
        :param key:
        :return: None
        """
        return bool(self.redis.exists(key))
