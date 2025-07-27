import logging
from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from .db.redis import RedisClient, RedisConfig
from .integrations.reccobeats import ReccoBeatsClient, ReccoBeatsConfig
from .integrations.spotify import SpotifyClient, SpotifyConfig
from .playlists import PlaylistRepo, PlaylistService

logger = logging.getLogger(__name__)


# Configuration dependencies
@lru_cache
def get_redis_config() -> RedisConfig:
    """Get Redis configuration."""
    return RedisConfig.from_env()


@lru_cache
def get_spotify_config() -> SpotifyConfig:
    """Get Spotify configuration."""
    return SpotifyConfig.from_env()


@lru_cache
def get_reccobeats_config() -> ReccoBeatsConfig:
    """Get ReccoBeats configuration."""
    return ReccoBeatsConfig.from_env()


# Client dependencies
@lru_cache
def get_redis_client(
    config: Annotated[RedisConfig, Depends(get_redis_config)],
) -> RedisClient:
    """Get Redis client instance."""
    return RedisClient(config.url)


@lru_cache
def get_spotify_client(
    config: Annotated[SpotifyConfig, Depends(get_spotify_config)],
) -> SpotifyClient:
    """Get Spotify client instance."""
    return SpotifyClient(config)


@lru_cache
def get_reccobeats_client(
    config: Annotated[ReccoBeatsConfig, Depends(get_reccobeats_config)],
) -> ReccoBeatsClient:
    """Get ReccoBeats client instance."""
    return ReccoBeatsClient(config)


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
) -> PlaylistService:
    """Get Playlist service instance."""
    return PlaylistService(spotify_client, reccobeats_client, playlist_repo)


# Type aliases for easier imports
RedisClientDep = Annotated[RedisClient, Depends(get_redis_client)]
RedisConfigDep = Annotated[RedisConfig, Depends(get_redis_config)]
SpotifyClientDep = Annotated[SpotifyClient, Depends(get_spotify_client)]
ReccoBeatsClientDep = Annotated[ReccoBeatsClient, Depends(get_reccobeats_client)]
PlaylistRepoDep = Annotated[PlaylistRepo, Depends(get_playlist_repo)]
PlaylistServiceDep = Annotated[PlaylistService, Depends(get_playlist_service)]
