import hashlib
import json
import logging
from collections.abc import Callable
from typing import Any

from ..db.redis import RedisClient

logger = logging.getLogger(__name__)


class PlaylistRepo:
    """
    Repository for playlist-related data with Redis caching.
    Uses callback pattern to handle cache-miss scenarios.
    """

    def __init__(self, redis_client: RedisClient):
        self.redis_client = redis_client

    def _generate_cache_key(self, prefix: str, **kwargs) -> str:
        """Generate a consistent cache key from parameters."""
        # Create a deterministic string from the parameters
        params_str = json.dumps(kwargs, sort_keys=True)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()
        return f"{prefix}:{params_hash}"

    async def get_or_fetch_spotify_tracks(
        self,
        query: str,
        limit: int,
        offset: int,
        fetch_callback: Callable[[], list[dict[str, Any]]],
    ) -> list[dict[str, Any]]:
        """
        Get Spotify tracks from cache or fetch using callback.

        Args:
            query: Search query
            limit: Number of tracks to return
            offset: Offset for pagination
            fetch_callback: Function to call if cache miss (should return track list)

        Returns:
            List of track dictionaries
        """
        cache_key = self._generate_cache_key(
            "spotify_search", query=query, limit=limit, offset=offset
        )

        # Try to get from cache first
        cached_data = await self.redis_client.get_json(cache_key)
        if cached_data is not None:
            logger.info(
                f"Cache hit for Spotify search: {query} (limit={limit}, offset={offset})"
            )
            return cached_data

        logger.info(
            f"Cache miss for Spotify search: {query} (limit={limit}, offset={offset})"
        )

        # Cache miss - use callback to fetch data
        try:
            fresh_data = fetch_callback()

            # Store in cache (no expiration for persistent storage)
            await self.redis_client.set_json(cache_key, fresh_data)
            logger.info(f"Cached Spotify search results for: {query}")

            return fresh_data

        except Exception as e:
            logger.error(f"Failed to fetch Spotify tracks via callback: {e}")
            return []

    async def get_or_fetch_spotify_audio_features(
        self,
        track_ids: list[str],
        fetch_callback: Callable[[], dict[str, dict[str, Any]]],
    ) -> dict[str, dict[str, Any]]:
        """
        Get Spotify audio features from cache or fetch using callback.

        Args:
            track_ids: List of Spotify track IDs
            fetch_callback: Function to call if cache miss (should return features dict)

        Returns:
            Dictionary mapping track_id to audio features
        """
        # For audio features, we'll cache individually to allow partial hits
        features_map = {}
        missing_ids = []

        # Check cache for each track ID
        for track_id in track_ids:
            cache_key = self._generate_cache_key(
                "spotify_audio_features", track_id=track_id
            )
            cached_features = await self.redis_client.get_json(cache_key)

            if cached_features is not None:
                features_map[track_id] = cached_features
            else:
                missing_ids.append(track_id)

        if missing_ids:
            logger.info(f"Cache miss for {len(missing_ids)} Spotify audio features")

            # Fetch missing features via callback
            try:
                fresh_features = fetch_callback()

                # Cache each individual feature set
                for track_id, features in fresh_features.items():
                    if (
                        track_id in missing_ids
                    ):  # Only cache the ones we actually requested
                        cache_key = self._generate_cache_key(
                            "spotify_audio_features", track_id=track_id
                        )
                        await self.redis_client.set_json(cache_key, features)

                # Merge with cached results
                features_map.update(fresh_features)
                logger.info(f"Cached audio features for {len(fresh_features)} tracks")

            except Exception as e:
                logger.error(f"Failed to fetch audio features via callback: {e}")

        logger.info(
            f"Returning audio features for {len(features_map)}/{len(track_ids)} requested tracks"
        )
        return features_map

    async def get_or_fetch_reccobeats_metadata(
        self, spotify_ids: list[str], fetch_callback: Callable[[], dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Get ReccoBeats metadata from cache or fetch using callback.

        Args:
            spotify_ids: List of Spotify track IDs
            fetch_callback: Function to call if cache miss

        Returns:
            Dictionary mapping spotify_id to ReccoBeats data
        """
        metadata_map = {}
        missing_ids = []

        # Check cache for each Spotify ID
        for spotify_id in spotify_ids:
            cache_key = self._generate_cache_key(
                "reccobeats_metadata", spotify_id=spotify_id
            )
            cached_metadata = await self.redis_client.get_json(cache_key)

            if cached_metadata is not None:
                metadata_map[spotify_id] = cached_metadata
            else:
                missing_ids.append(spotify_id)

        if missing_ids:
            logger.info(
                f"Cache miss for {len(missing_ids)} ReccoBeats metadata entries"
            )

            # Fetch missing metadata via callback
            try:
                fresh_metadata = fetch_callback()

                # Cache each individual metadata entry
                for spotify_id, metadata in fresh_metadata.items():
                    if spotify_id in missing_ids:
                        cache_key = self._generate_cache_key(
                            "reccobeats_metadata", spotify_id=spotify_id
                        )
                        await self.redis_client.set_json(cache_key, metadata)

                # Merge with cached results
                metadata_map.update(fresh_metadata)
                logger.info(
                    f"Cached ReccoBeats metadata for {len(fresh_metadata)} tracks"
                )

            except Exception as e:
                logger.error(f"Failed to fetch ReccoBeats metadata via callback: {e}")

        logger.info(
            f"Returning ReccoBeats metadata for {len(metadata_map)}/{len(spotify_ids)} requested tracks"
        )
        return metadata_map

    async def get_or_fetch_reccobeats_audio_features(
        self, reccobeats_ids: list[str], fetch_callback: Callable[[], dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Get ReccoBeats audio features from cache or fetch using callback.

        Args:
            reccobeats_ids: List of ReccoBeats track IDs
            fetch_callback: Function to call if cache miss

        Returns:
            Dictionary mapping reccobeats_id to audio features
        """
        features_map = {}
        missing_ids = []

        # Check cache for each ReccoBeats ID
        for reccobeats_id in reccobeats_ids:
            cache_key = self._generate_cache_key(
                "reccobeats_audio_features", reccobeats_id=reccobeats_id
            )
            cached_features = await self.redis_client.get_json(cache_key)

            if cached_features is not None:
                features_map[reccobeats_id] = cached_features
            else:
                missing_ids.append(reccobeats_id)

        if missing_ids:
            logger.info(f"Cache miss for {len(missing_ids)} ReccoBeats audio features")

            # Fetch missing features via callback
            try:
                fresh_features = fetch_callback()

                # Cache each individual feature set
                for reccobeats_id, features in fresh_features.items():
                    if reccobeats_id in missing_ids:
                        cache_key = self._generate_cache_key(
                            "reccobeats_audio_features", reccobeats_id=reccobeats_id
                        )
                        await self.redis_client.set_json(cache_key, features)

                # Merge with cached results
                features_map.update(fresh_features)
                logger.info(
                    f"Cached ReccoBeats audio features for {len(fresh_features)} tracks"
                )

            except Exception as e:
                logger.error(
                    f"Failed to fetch ReccoBeats audio features via callback: {e}"
                )

        logger.info(
            f"Returning ReccoBeats audio features for {len(features_map)}/{len(reccobeats_ids)} requested tracks"
        )
        return features_map

    async def store_generated_playlist(
        self,
        activity: str,
        vibe: str,
        duration_minutes: int,
        playlist_data: dict[str, Any],
    ) -> bool:
        """
        Store a generated playlist for potential future reuse.

        Args:
            activity: Activity type
            vibe: Vibe type
            duration_minutes: Target duration
            playlist_data: Complete playlist response data

        Returns:
            True if stored successfully
        """
        cache_key = self._generate_cache_key(
            "generated_playlist",
            activity=activity,
            vibe=vibe,
            duration_minutes=duration_minutes,
        )

        try:
            success = await self.redis_client.set_json(cache_key, playlist_data)
            if success:
                logger.info(
                    f"Stored generated playlist: {activity}-{vibe}-{duration_minutes}min"
                )
            return success
        except Exception as e:
            logger.error(f"Failed to store generated playlist: {e}")
            return False

    async def get_generated_playlist(
        self, activity: str, vibe: str, duration_minutes: int
    ) -> dict[str, Any] | None:
        """
        Get a previously generated playlist if it exists.

        Args:
            activity: Activity type
            vibe: Vibe type
            duration_minutes: Target duration

        Returns:
            Playlist data if found, None otherwise
        """
        cache_key = self._generate_cache_key(
            "generated_playlist",
            activity=activity,
            vibe=vibe,
            duration_minutes=duration_minutes,
        )

        try:
            cached_playlist = await self.redis_client.get_json(cache_key)
            if cached_playlist:
                logger.info(
                    f"Found cached playlist: {activity}-{vibe}-{duration_minutes}min"
                )
            return cached_playlist
        except Exception as e:
            logger.error(f"Failed to get cached playlist: {e}")
            return None

    async def clear_cache(self, pattern: str = "*") -> int:
        """
        Clear cached data matching pattern.

        Args:
            pattern: Redis key pattern to match

        Returns:
            Number of keys deleted
        """
        try:
            keys = await self.redis_client.keys(pattern)
            deleted_count = 0

            for key in keys:
                if await self.redis_client.delete(key):
                    deleted_count += 1

            logger.info(
                f"Cleared {deleted_count} cache entries matching pattern: {pattern}"
            )
            return deleted_count

        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return 0
