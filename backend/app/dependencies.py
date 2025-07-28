import logging
from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from .db.redis import RedisClient, RedisConfig
from .integrations.reccobeats import ReccoBeatsClient, ReccoBeatsConfig
from .integrations.spotify import SpotifyClient, SpotifyConfig
from .integrations.gemini import GeminiClient
from .playlists import PlaylistRepo, PlaylistService

logger = logging.getLogger(__name__)

# Global instances for caching
_redis_config = None
_spotify_config = None
_reccobeats_config = None
_redis_client = None
_spotify_client = None
_reccobeats_client = None
_gemini_client = None

# Configuration dependencies
def get_redis_config() -> RedisConfig:
    """Get Redis configuration."""
    global _redis_config
    if _redis_config is None:
        _redis_config = RedisConfig.from_env()
    return _redis_config


def get_spotify_config() -> SpotifyConfig:
    """Get Spotify configuration."""
    global _spotify_config
    if _spotify_config is None:
        _spotify_config = SpotifyConfig.from_env()
    return _spotify_config


def get_reccobeats_config() -> ReccoBeatsConfig:
    """Get ReccoBeats configuration."""
    global _reccobeats_config
    if _reccobeats_config is None:
        _reccobeats_config = ReccoBeatsConfig.from_env()
    return _reccobeats_config


# Client dependencies
def get_redis_client(
        config: Annotated[RedisConfig, Depends(get_redis_config)],
) -> RedisClient:
    """Get Redis client instance."""
    global _redis_client
    if _redis_client is None:
        _redis_client = RedisClient(config.url)
    return _redis_client


def get_spotify_client(
        config: Annotated[SpotifyConfig, Depends(get_spotify_config)],
) -> SpotifyClient:
    """Get Spotify client instance."""
    global _spotify_client
    if _spotify_client is None:
        _spotify_client = SpotifyClient(config)
    return _spotify_client


def get_reccobeats_client(
        config: Annotated[ReccoBeatsConfig, Depends(get_reccobeats_config)],
) -> ReccoBeatsClient:
    """Get ReccoBeats client instance."""
    global _reccobeats_client
    if _reccobeats_client is None:
        _reccobeats_client = ReccoBeatsClient(config)
    return _reccobeats_client


def get_gemini_client() -> GeminiClient:
    """Get Gemini client instance."""
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client


# Repository dependencies
def get_playlist_repo(
        redis_client: Annotated[RedisClient, Depends(get_redis_client)],
) -> PlaylistRepo:
    """Get Playlist repository instance."""
    return PlaylistRepo(redis_client)


# Service dependencies
def get_playlist_service(
        spotify_client: Annotated[SpotifyClient, Depends(get_spotify_client)],
        reccobeats_client: Annotated[ReccoBeatsClient, Depends(get_reccobeats_client)],
        playlist_repo: Annotated[PlaylistRepo, Depends(get_playlist_repo)],
        gemini_client: Annotated[GeminiClient, Depends(get_gemini_client)],
) -> PlaylistService:
    """Get Playlist service instance."""
    return PlaylistService(spotify_client, reccobeats_client, playlist_repo, gemini_client)


# Type aliases for easier imports
RedisClientDep = Annotated[RedisClient, Depends(get_redis_client)]
RedisConfigDep = Annotated[RedisConfig, Depends(get_redis_config)]
SpotifyClientDep = Annotated[SpotifyClient, Depends(get_spotify_client)]
ReccoBeatsClientDep = Annotated[ReccoBeatsClient, Depends(get_reccobeats_client)]
PlaylistRepoDep = Annotated[PlaylistRepo, Depends(get_playlist_repo)]
PlaylistServiceDep = Annotated[PlaylistService, Depends(get_playlist_service)]