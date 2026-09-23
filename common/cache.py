"""
Thin Redis wrapper providing a @cached decorator, equivalent to Spring's
@Cacheable / @CacheEvict annotations used in the Java services.
"""
import json
import os
from functools import wraps

import redis

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_DB = int(os.environ.get("REDIS_DB", 0))

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)


def cached(prefix: str, ttl_seconds: int = 300):
    """
    Cache a function's JSON-serializable return value in Redis.
    Cache key = f"{prefix}:{first_positional_arg}".
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            key_part = args[0] if args else "all"
            cache_key = f"{prefix}:{key_part}"
            cached_value = redis_client.get(cache_key)
            if cached_value is not None:
                return json.loads(cached_value)

            result = fn(*args, **kwargs)
            redis_client.setex(cache_key, ttl_seconds, json.dumps(result, default=str))
            return result
        return wrapper
    return decorator


def evict(prefix: str, key_part=None):
    """Evict one cache key, or every key under a prefix when key_part is None."""
    if key_part is not None:
        redis_client.delete(f"{prefix}:{key_part}")
    else:
        for key in redis_client.scan_iter(f"{prefix}:*"):
            redis_client.delete(key)
