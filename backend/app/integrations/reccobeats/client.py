import http.client
import json
import logging
import urllib.parse
from typing import Any

from .config import ReccoBeatsConfig

logger = logging.getLogger(__name__)


class ReccoBeatsClient:
    """
    Client for ReccoBeats API operations.
    Handles track metadata and audio features fetching.
    """

    def __init__(self, config: ReccoBeatsConfig):
        self.config = config
        self._audio_features_cache: dict[str, Any] = {}

    def fetch_metadata_batch(self, spotify_ids: list[str]) -> dict[str, Any]:
        """
        Fetch basic track metadata from ReccoBeats API for a batch of Spotify IDs.
        Returns a dictionary mapping original Spotify ID to its ReccoBeats ID and metadata.
        """
        spotify_to_reccobeats_map = {}
        logger.info(f"Fetching ReccoBeats metadata for {len(spotify_ids)} Spotify IDs")

        try:
            conn = http.client.HTTPSConnection(self.config.base_url)

            for spotify_id in spotify_ids:
                url = f"/tracks/spotify/{urllib.parse.quote(spotify_id)}"
                conn.request("GET", url)
                response = conn.getresponse()

                if response.status == 200:
                    data = json.loads(response.read().decode())
                    if data.get("success") and data.get("track"):
                        track_data = data["track"]
                        reccobeats_id = track_data.get("id")
                        spotify_to_reccobeats_map[spotify_id] = {
                            "reccobeats_id": reccobeats_id,
                            "metadata": track_data,
                        }
                else:
                    logger.warning(
                        f"ReccoBeats API returned status {response.status} for Spotify ID {spotify_id}"
                    )

            conn.close()
            logger.info(
                f"Successfully mapped {len(spotify_to_reccobeats_map)}/{len(spotify_ids)} tracks"
            )

        except Exception as e:
            logger.error(f"Error fetching ReccoBeats metadata: {e}")

        return spotify_to_reccobeats_map

    def fetch_audio_features_batch(self, reccobeats_ids: list[str]) -> dict[str, Any]:
        """
        Fetch detailed audio features from ReccoBeats API for a batch of ReccoBeats IDs.
        Returns a dictionary mapping ReccoBeats ID to its audio features.
        """
        features_map = {}
        logger.info(f"Fetching audio features for {len(reccobeats_ids)} ReccoBeats IDs")

        try:
            conn = http.client.HTTPSConnection(self.config.base_url)

            for reccobeats_id in reccobeats_ids:
                # Check cache first
                if reccobeats_id in self._audio_features_cache:
                    features_map[reccobeats_id] = self._audio_features_cache[
                        reccobeats_id
                    ]
                    continue

                url = f"/audio-features/{urllib.parse.quote(str(reccobeats_id))}"
                conn.request("GET", url)
                response = conn.getresponse()

                if response.status == 200:
                    data = json.loads(response.read().decode())
                    if data.get("success") and data.get("audioFeatures"):
                        audio_features = data["audioFeatures"]
                        features_map[reccobeats_id] = audio_features
                        # Cache the result
                        self._audio_features_cache[reccobeats_id] = audio_features
                else:
                    logger.warning(
                        f"ReccoBeats API returned status {response.status} for ID {reccobeats_id}"
                    )

            conn.close()
            logger.info(
                f"Successfully fetched audio features for {len(features_map)}/{len(reccobeats_ids)} tracks"
            )

        except Exception as e:
            logger.error(f"Error fetching ReccoBeats audio features: {e}")

        return features_map

    def get_combined_track_data(self, spotify_ids: list[str]) -> dict[str, Any]:
        """
        Get both metadata and audio features for Spotify tracks.
        Returns a dictionary mapping Spotify ID to combined data.
        """
        # First, get metadata and ReccoBeats IDs
        metadata_map = self.fetch_metadata_batch(spotify_ids)

        # Extract ReccoBeats IDs for audio features request
        reccobeats_ids = [
            data["reccobeats_id"]
            for data in metadata_map.values()
            if data.get("reccobeats_id")
        ]

        # Get audio features
        audio_features_map = self.fetch_audio_features_batch(reccobeats_ids)

        # Combine the data
        combined_data = {}
        for spotify_id, metadata_info in metadata_map.items():
            reccobeats_id = metadata_info.get("reccobeats_id")
            combined_data[spotify_id] = {
                "metadata": metadata_info.get("metadata", {}),
                "audio_features": audio_features_map.get(reccobeats_id, {})
                if reccobeats_id
                else {},
            }

        return combined_data

    def clear_cache(self) -> None:
        """Clear the audio features cache."""
        self._audio_features_cache.clear()
        logger.info("ReccoBeats audio features cache cleared")
