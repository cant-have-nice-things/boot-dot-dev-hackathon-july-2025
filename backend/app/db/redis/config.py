import os

from pydantic import BaseModel


class RedisConfig(BaseModel):
    """Redis connection configuration."""

    url: str = "redis://localhost:6379/0"
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: str | None = None

    # Connection settings
    max_connections: int = 10
    retry_on_timeout: bool = True

    @classmethod
    def from_env(cls) -> "RedisConfig":
        """Create configuration from environment variables."""
        return cls(
            url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            db=int(os.getenv("REDIS_DB", "0")),
            password=os.getenv("REDIS_PASSWORD"),
            max_connections=int(os.getenv("REDIS_MAX_CONNECTIONS", "10")),
        )
