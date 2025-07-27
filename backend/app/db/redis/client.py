import json
import logging

import redis.asyncio as redis

logger = logging.getLogger(__name__)


class RedisClient:
    """
    Simple async Redis client wrapper.
    Provides basic Redis operations without business logic.
    """

    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self._redis: redis.Redis | None = None

    async def connect(self) -> None:
        """Establish connection to Redis."""
        try:
            self._redis = redis.from_url(self.redis_url)
            await self._redis.ping()
            logger.info("Successfully connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            logger.info("Redis connection closed")

    @property
    def redis(self) -> redis.Redis:
        """Get the Redis instance."""
        if self._redis is None:
            raise RuntimeError("Redis client not connected. Call connect() first.")
        return self._redis

    async def ping(self) -> bool:
        """Test Redis connection."""
        try:
            return await self.redis.ping()
        except Exception as e:
            logger.error(f"Redis ping failed: {e}")
            return False

    # String operations
    async def get(self, key: str) -> str | None:
        """Get string value by key."""
        try:
            result = await self.redis.get(key)
            return result.decode() if result else None
        except Exception as e:
            logger.error(f"Failed to get key {key}: {e}")
            return None

    async def set(
        self, key: str, value: str, expire_seconds: int | None = None
    ) -> bool:
        """Set key-value pair with optional expiration."""
        try:
            return await self.redis.set(key, value, ex=expire_seconds)
        except Exception as e:
            logger.error(f"Failed to set key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key."""
        try:
            result = await self.redis.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Failed to delete key {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            logger.error(f"Failed to check existence of key {key}: {e}")
            return False

    # JSON operations (convenience methods)
    async def get_json(self, key: str) -> dict | None:
        """Get JSON value by key."""
        try:
            value = await self.get(key)
            if value:
                return json.loads(value)
            return None
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Failed to get JSON for key {key}: {e}")
            return None

    async def set_json(
        self, key: str, value: dict, expire_seconds: int | None = None
    ) -> bool:
        """Set JSON value with optional expiration."""
        try:
            json_str = json.dumps(value)
            return await self.set(key, json_str, expire_seconds)
        except Exception as e:
            logger.error(f"Failed to set JSON for key {key}: {e}")
            return False

    # List operations
    async def lpush(self, key: str, *values: str) -> int | None:
        """Push values to the left of a list."""
        try:
            return await self.redis.lpush(key, *values)
        except Exception as e:
            logger.error(f"Failed to lpush to key {key}: {e}")
            return None

    async def rpush(self, key: str, *values: str) -> int | None:
        """Push values to the right of a list."""
        try:
            return await self.redis.rpush(key, *values)
        except Exception as e:
            logger.error(f"Failed to rpush to key {key}: {e}")
            return None

    async def lrange(self, key: str, start: int = 0, end: int = -1) -> list[str]:
        """Get list elements in range."""
        try:
            result = await self.redis.lrange(key, start, end)
            return [
                item.decode() if isinstance(item, bytes) else item for item in result
            ]
        except Exception as e:
            logger.error(f"Failed to lrange key {key}: {e}")
            return []

    async def llen(self, key: str) -> int:
        """Get list length."""
        try:
            return await self.redis.llen(key)
        except Exception as e:
            logger.error(f"Failed to get length of key {key}: {e}")
            return 0

    # Hash operations
    async def hget(self, key: str, field: str) -> str | None:
        """Get hash field value."""
        try:
            result = await self.redis.hget(key, field)
            return result.decode() if result else None
        except Exception as e:
            logger.error(f"Failed to hget {field} from key {key}: {e}")
            return None

    async def hset(self, key: str, field: str, value: str) -> bool:
        """Set hash field value."""
        try:
            return await self.redis.hset(key, field, value) >= 0
        except Exception as e:
            logger.error(f"Failed to hset {field} in key {key}: {e}")
            return False

    async def hgetall(self, key: str) -> dict[str, str]:
        """Get all hash fields and values."""
        try:
            result = await self.redis.hgetall(key)
            return {
                k.decode() if isinstance(k, bytes) else k: v.decode()
                if isinstance(v, bytes)
                else v
                for k, v in result.items()
            }
        except Exception as e:
            logger.error(f"Failed to hgetall for key {key}: {e}")
            return {}

    async def hdel(self, key: str, *fields: str) -> int:
        """Delete hash fields."""
        try:
            return await self.redis.hdel(key, *fields)
        except Exception as e:
            logger.error(f"Failed to hdel fields from key {key}: {e}")
            return 0

    # Set operations
    async def sadd(self, key: str, *members: str) -> int:
        """Add members to a set."""
        try:
            return await self.redis.sadd(key, *members)
        except Exception as e:
            logger.error(f"Failed to sadd to key {key}: {e}")
            return 0

    async def smembers(self, key: str) -> set[str]:
        """Get all set members."""
        try:
            result = await self.redis.smembers(key)
            return {
                item.decode() if isinstance(item, bytes) else item for item in result
            }
        except Exception as e:
            logger.error(f"Failed to smembers for key {key}: {e}")
            return set()

    async def srem(self, key: str, *members: str) -> int:
        """Remove members from a set."""
        try:
            return await self.redis.srem(key, *members)
        except Exception as e:
            logger.error(f"Failed to srem from key {key}: {e}")
            return 0

    # Utility operations
    async def increment(self, key: str, amount: int = 1) -> int | None:
        """Increment a counter."""
        try:
            return await self.redis.incrby(key, amount)
        except Exception as e:
            logger.error(f"Failed to increment key {key}: {e}")
            return None

    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration on existing key."""
        try:
            return await self.redis.expire(key, seconds)
        except Exception as e:
            logger.error(f"Failed to set expiration on key {key}: {e}")
            return False

    async def keys(self, pattern: str = "*") -> list[str]:
        """Get keys matching pattern."""
        try:
            keys = await self.redis.keys(pattern)
            return [key.decode() if isinstance(key, bytes) else key for key in keys]
        except Exception as e:
            logger.error(f"Failed to get keys with pattern {pattern}: {e}")
            return []
