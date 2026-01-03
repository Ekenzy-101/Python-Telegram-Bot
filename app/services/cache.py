import json
import redis
from app.config import settings
from datetime import timedelta
from typing import Any


class CacheService:
    """Manages cache data"""

    def __init__(self, user_id: int):
        self.cache = redis.Redis.from_url(settings.redis_url)
        self.user_id = user_id

    def read(self, namespace: str, default: Any = None) -> Any:
        """Read user session data from cache"""
        value = self.cache.get(f"user:{self.user_id}:{namespace}")
        if value:
            return json.loads(value)
        return default

    def read_config(self) -> Any:
        """Read client config from cache"""
        value = self.cache.get("client_config")
        if value:
            return json.loads(value)
        return None

    def save(self, namespace: str, value: Any, ttl: Any | timedelta = None) -> str:
        """Save user session data to cache"""
        if isinstance(value, dict) or isinstance(value, list):
            value = json.dumps(value)
        result = self.cache.set(f"user:{self.user_id}:{namespace}", value)
        if result and ttl:
            return self.cache.expire(f"user:{self.user_id}:{namespace}", ttl)
        return result
