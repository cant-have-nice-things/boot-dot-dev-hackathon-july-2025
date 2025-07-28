import base64
import logging
import os
from typing import Any

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from .config import SpotifyConfig

logger = logging.getLogger(__name__)


class SpotifyClient:
    """
    Client for Spotify API operations.
    Handles authentication and basic Spotify API calls.
    """

    def __init__(self, config: SpotifyConfig):
        self.config = config
        self.sp: spotipy.Spotify | None = None
        self.user_id: str | None = None
        self.auth_manager: SpotifyClientCredentials | None = None

    async def connect(self) -> bool:
        """Initialize Spotify connection and authenticate."""
        try:
            self.auth_manager = SpotifyClientCredentials(
                client_id=self.config.client_id,
                client_secret=self.config.client_secret,
            )

            self.sp = spotipy.Spotify(auth_manager=self.auth_manager)
            self.user_id = "me"  # Not a real user, but needed for some calls

            logger.info(
                f"Successfully authenticated Spotify client with client credentials"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to connect to Spotify: {e}")
            self.sp = None
            self.user_id = None
            return False

    def is_connected(self) -> bool:
        """Check if client is connected and authenticated."""
        return self.sp is not None and self.user_id is not None

    def search_tracks(
        self, query: str, limit: int = 50, offset: int = 0
    ) -> list[dict[str, Any]]:
        """Search for tracks on Spotify."""
        if not self.is_connected():
            raise RuntimeError("Spotify client not connected")

        try:
            results = self.sp.search(q=query, type="track", limit=limit, offset=offset)
            return results["tracks"]["items"]
        except Exception as e:
            logger.error(f"Failed to search tracks: {e}")
            return []

    def get_track_audio_features(
        self, track_ids: list[str]
    ) -> dict[str, dict[str, Any]]:
        """Get audio features for a list of track IDs."""
        if not self.is_connected():
            raise RuntimeError("Spotify client not connected")

        try:
            # Spotify API allows max 100 tracks per request
            features_map = {}

            for i in range(0, len(track_ids), 100):
                batch = track_ids[i : i + 100]
                features = self.sp.audio_features(batch)

                for j, feature in enumerate(features):
                    if feature:  # feature can be None if track not found
                        features_map[batch[j]] = feature

            return features_map
        except Exception as e:
            logger.error(f"Failed to get audio features: {e}")
            return {}

    def create_playlist(
        self, name: str, description: str = "", public: bool = True
    ) -> dict[str, Any] | None:
        """Create a new playlist."""
        if not self.is_connected():
            raise RuntimeError("Spotify client not connected")

        try:
            playlist = self.sp.user_playlist_create(
                user=self.user_id, name=name, public=public, description=description
            )
            logger.info(f"Created playlist: {playlist['name']} (ID: {playlist['id']})")
            return playlist
        except Exception as e:
            logger.error(f"Failed to create playlist: {e}")
            return None

    def add_tracks_to_playlist(self, playlist_id: str, track_uris: list[str]) -> bool:
        """Add tracks to a playlist."""
        if not self.is_connected():
            raise RuntimeError("Spotify client not connected")

        try:
            # Spotify API allows max 100 tracks per request
            for i in range(0, len(track_uris), 100):
                batch = track_uris[i : i + 100]
                self.sp.playlist_add_items(playlist_id, batch)

            logger.info(f"Added {len(track_uris)} tracks to playlist {playlist_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add tracks to playlist: {e}")
            return False

    def upload_playlist_cover(self, playlist_id: str, image_path: str) -> bool:
        """Upload cover image to a playlist."""
        if not self.is_connected():
            raise RuntimeError("Spotify client not connected")

        try:
            if not os.path.exists(image_path):
                logger.warning(f"Image file not found: {image_path}")
                return False

            with open(image_path, "rb") as img_file:
                image_data = img_file.read()

            return self.upload_playlist_cover_image_data(playlist_id, image_data)

        except Exception as e:
            logger.error(f"Failed to upload playlist cover: {e}")
            return False

    def upload_playlist_cover_image_data(self, playlist_id: str, image_data: bytes) -> bool:
        """Upload cover image data to a playlist."""
        if not self.is_connected():
            raise RuntimeError("Spotify client not connected")

        try:
            image_data_base64 = base64.b64encode(image_data).decode("utf-8")
            self.sp.playlist_upload_cover_image(playlist_id, image_data_base64)

            logger.info(f"Uploaded cover image for playlist {playlist_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to upload playlist cover: {e}")
            return False

    def get_playlist(self, playlist_id: str) -> dict[str, Any] | None:
        """Get playlist details."""
        if not self.is_connected():
            raise RuntimeError("Spotify client not connected")

        try:
            return self.sp.playlist(playlist_id)
        except Exception as e:
            logger.error(f"Failed to get playlist {playlist_id}: {e}")
            return None
