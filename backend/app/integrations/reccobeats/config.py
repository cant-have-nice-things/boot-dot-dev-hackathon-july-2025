import os

from pydantic import BaseModel


class ReccoBeatsConfig(BaseModel):
    """ReccoBeats API configuration."""

    base_url: str = "reccobeats.com"
    timeout: int = 30

    @classmethod
    def from_env(cls) -> "ReccoBeatsConfig":
        """Create configuration from environment variables."""
        return cls(
            base_url=os.getenv("RECCOBEATS_BASE_URL", "reccobeats.com"),
            timeout=int(os.getenv("RECCOBEATS_TIMEOUT", "30")),
        )
