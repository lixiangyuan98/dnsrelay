"""Cache interface and implementation."""
import redis

from typing import *
from util.log import logger
from . import settings


class BaseCache:
    """Interface for cache."""

    def get(self, key: str, field: str) -> Any:
        raise NotImplementedError
    
    def put(self, key: str, field: str, value: str) -> Any:
        raise NotImplementedError
    
    def get_ttl(self, key: str) -> Any:
        raise NotImplementedError

    def set_ttl(self, key: str, ttl: int) -> Any:
        raise NotImplementedError
    
    def del_key(self, key: str) -> Any:
        raise NotImplementedError
    
    def del_record(self, key: str, field: str) -> Any:
        raise NotImplementedError


class RedisCache(BaseCache):
    """Redis caching implementation."""

    _host = getattr(settings, 'redis_host') if hasattr(settings, 'redis_host') else 'localhost'
    _port = getattr(settings, 'redis_port') if hasattr(settings, 'redis_port') else 6379
    _db = getattr(settings, 'redis_db') if hasattr(settings, 'redis_db') else 0
    _pool = redis.BlockingConnectionPool(host=_host, port=_port, db=_db)
    logger.info('Create Redis connection pool %s', _pool)

    def __init__(self):
        self._connection = redis.Redis(connection_pool=RedisCache._pool)
    
    def get(self, key: str, field: str=None) -> Union[bytes, dict]:
        if field is not None:
            return self._connection.hget(key, field)
        else:
            return self._connection.hgetall(key)
    
    def put(self, key: str, field: str, value: str) -> int:
        return self._connection.hset(key, field, value)
    
    def get_ttl(self, key: str) -> int:
        return self._connection.ttl(key)

    def set_ttl(self, key: str, ttl: int) -> None:
        if ttl == -1:
            self._connection.persist(key)
        else:
            self._connection.expire(key, ttl)
    
    def del_record(self, key: str, field: str) -> None:
        return self._connection.hdel(key, field)
    
    def del_key(self, key):
        return self._connection.delete(key)
