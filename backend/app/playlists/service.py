import logging
import os
import random
from typing import Any

from ..integrations.reccobeats import ReccoBeatsClient
from ..integrations.spotify import SpotifyClient
from .repo import PlaylistRepo

logger = logging.getLogger(__name__)


class PlaylistService:
    """
    Service for creating and managing playlists.
    Orchestrates Spotify and ReccoBeats clients with caching via PlaylistRepo.
    """

    def __init__(
        self,
        spotify_client: SpotifyClient,
        reccobeats_client: ReccoBeatsClient,
        playlist_repo: PlaylistRepo,
    ):
        self.spotify_client = spotify_client
        self.reccobeats_client = reccobeats_client
        self.playlist_repo = playlist_repo

    async def create_activity_playlist(
        self, activity: str, vibe: str, duration_minutes: int = 30
    ) -> dict[str, Any]:
        """
        Create a playlist based on activity, vibe, and duration.

        Args:
            activity: The activity type (e.g., "yoga", "studying", "cleaning")
            vibe: The desired vibe (e.g., "chill", "upbeat")
            duration_minutes: Target playlist duration in minutes

        Returns:
            Dictionary containing playlist data and metadata
        """
        if not self.spotify_client.is_connected():
            return {
                "error": "Spotify service not authenticated. Cannot create playlist."
            }

        logger.info(
            f"Creating playlist for {activity} with {vibe} vibe, {duration_minutes} minutes"
        )

        # Check if we have a cached complete playlist for these exact parameters
        cached_playlist = await self.playlist_repo.get_generated_playlist(
            activity, vibe, duration_minutes
        )
        if cached_playlist:
            logger.info("Returning cached complete playlist")
            return cached_playlist

        # Search for tracks using repo (which handles caching)
        tracks = await self._search_tracks_by_criteria(
            activity=activity,
            vibe=vibe,
            duration_minutes=duration_minutes,
            total_fetch_limit=400,
        )

        if not tracks:
            logger.warning("No tracks found after search and filtering")
            return {"error": "No suitable tracks found"}

        # Format tracks for response
        formatted_tracks = self._format_tracks_for_response(tracks)

        if not formatted_tracks:
            logger.warning("No tracks remained after formatting")
            return {"error": "No suitable tracks with complete data found"}

        # Create Spotify playlist
        playlist_result = self._create_spotify_playlist(
            activity=activity,
            vibe=vibe,
            tracks=formatted_tracks,
            duration_minutes=duration_minutes,
        )

        if not playlist_result:
            return {"error": "Failed to create playlist on Spotify"}

        # Calculate total duration in minutes for response
        total_duration_minutes = sum(t.get("duration", 0) for t in formatted_tracks) / (
            1000 * 60
        )

        # Create the final response in the format expected by the API
        import time
        from datetime import datetime

        timestamp = int(time.time() * 1000)

        final_playlist_data = {
            "id": playlist_result.get("playlist_id", f"generated_playlist_{timestamp}"),
            "name": playlist_result.get(
                "playlist_name", f"{activity} - {vibe} Playlist"
            ),
            "description": playlist_result.get(
                "playlist_description",
                f"A {vibe} playlist for your {activity} session."
            ),
            "spotifyUrl": playlist_result.get("playlist_url", ""),
            "imageUrl": playlist_result.get(
                "playlist_image_url",
                "https://via.placeholder.com/300x300.png?text=Playlist+Image",
            ),
            "tracks": formatted_tracks,
            "duration": int(total_duration_minutes),
            "createdAt": datetime.now().isoformat(),
            # NEW: Include the original activity and vibe in the response
            "activity": activity,
            "vibe": vibe,
        }

        # Cache the complete playlist for future requests
        await self.playlist_repo.store_generated_playlist(
            activity, vibe, duration_minutes, final_playlist_data
        )

        playlist_id = final_playlist_data.get("id")
        logger.info(f"Attempting to store playlist with ID: {playlist_id}")
        logger.debug(f"Playlist data being stored (first 100 chars): {str(final_playlist_data)[:100]}...")
        if playlist_id:
            await self.playlist_repo.store_playlist_by_id(playlist_id, final_playlist_data)
            logger.info(f"Successfully called store_playlist_by_id for ID: {playlist_id}")
        else:
            logger.info(f"Failed store_playlist_by_id for ID: {playlist_id}")

        return final_playlist_data

    async def _search_tracks_by_criteria(
        self,
        activity: str,
        vibe: str,
        duration_minutes: int,
        total_fetch_limit: int = 400,
    ) -> list[dict[str, Any]]:
        """Search for tracks matching the given criteria using cached calls."""
        # Generate search queries based on activity and vibe
        search_queries = self._generate_search_queries(activity, vibe)

        all_tracks = []
        tracks_per_query = total_fetch_limit // len(search_queries)

        for query in search_queries:
            tracks = await self._fetch_tracks_for_query(query, limit=tracks_per_query)
            all_tracks.extend(tracks)

        # Remove duplicates based on track ID
        unique_tracks = {track["id"]: track for track in all_tracks if track.get("id")}
        tracks_list = list(unique_tracks.values())

        # Get audio features from ReccoBeats using repo
        filtered_tracks = await self._filter_tracks_by_audio_features(tracks_list, vibe)

        # Select tracks to match target duration
        selected_tracks = self._select_tracks_for_duration(
            filtered_tracks, duration_minutes
        )

        return selected_tracks

    def _generate_search_queries(self, activity: str, vibe: str) -> list[str]:
        """Generate search queries based on activity and vibe."""
        # Activity-based terms
        activity_terms = {
            "yoga": ["meditation", "zen", "relaxing", "peaceful", "ambient"],
            "studying": [
                "focus",
                "concentration",
                "instrumental",
                "ambient",
                "classical",
            ],
            "cleaning": ["energetic", "upbeat", "motivational", "pop", "dance"],
            "cooking": ["upbeat", "fun", "energetic", "happy", "pop"],
            "working out": [
                "energetic",
                "pump up",
                "workout",
                "fitness",
                "high energy",
            ],
            "running": ["running", "cardio", "high energy", "motivational", "upbeat"],
            "relaxing": ["chill", "ambient", "peaceful", "calm", "meditation"],
        }

        # Vibe-based terms
        vibe_terms = {
            "chill": ["chill", "relaxed", "mellow", "calm", "peaceful"],
            "upbeat": ["upbeat", "energetic", "happy", "positive", "lively"],
            "focus": ["instrumental", "ambient", "concentration", "study"],
            "energetic": ["high energy", "pump up", "motivational", "intense"],
        }

        queries = []

        # Combine activity and vibe terms
        activity_words = activity_terms.get(activity.lower(), [activity])
        vibe_words = vibe_terms.get(vibe.lower(), [vibe])

        for activity_word in activity_words:
            for vibe_word in vibe_words:
                queries.append(f"{activity_word} {vibe_word}")

        # Add some genre-based queries
        if vibe.lower() == "chill":
            queries.extend(["ambient", "chillout", "downtempo", "lo-fi"])
        elif vibe.lower() == "upbeat":
            queries.extend(["pop", "dance", "electronic", "indie pop"])

        return queries[:8]  # Limit to 8 queries to avoid too many API calls

    async def _fetch_tracks_for_query(
        self, query: str, limit: int
    ) -> list[dict[str, Any]]:
        """Fetch tracks for a single search query using repo caching."""
        try:
            tracks = []
            searches_per_query = 3  # Multiple searches with different offsets
            tracks_per_search = min(50, limit // searches_per_query)

            for i in range(searches_per_query):
                current_offset = i * tracks_per_search

                # Use repo with callback pattern - capture offset in closure
                def make_fetch_callback(q: str, limit_val: int, offset_val: int):
                    return lambda: self.spotify_client.search_tracks(
                        query=q, limit=limit_val, offset=offset_val
                    )

                batch = await self.playlist_repo.get_or_fetch_spotify_tracks(
                    query=query,
                    limit=tracks_per_search,
                    offset=current_offset,
                    fetch_callback=make_fetch_callback(
                        query, tracks_per_search, current_offset
                    ),
                )
                tracks.extend(batch)

                if len(tracks) >= limit:
                    break

            return tracks[:limit]

        except Exception as e:
            logger.error(f"Error fetching tracks for query '{query}': {e}")
            return []

    async def _filter_tracks_by_audio_features(
        self, tracks: list[dict[str, Any]], vibe: str
    ) -> list[dict[str, Any]]:
        """Filter tracks based on audio features from ReccoBeats using repo caching."""
        if not tracks:
            return []

        # Get Spotify IDs
        spotify_ids = [track["id"] for track in tracks if track.get("id")]

        # Get ReccoBeats metadata using repo with callback
        reccobeats_metadata = await self.playlist_repo.get_or_fetch_reccobeats_metadata(
            spotify_ids=spotify_ids,
            fetch_callback=lambda: self.reccobeats_client.fetch_metadata_batch(
                spotify_ids
            ),
        )

        # Extract ReccoBeats IDs for audio features
        reccobeats_ids = [
            data["reccobeats_id"]
            for data in reccobeats_metadata.values()
            if data.get("reccobeats_id")
        ]

        if not reccobeats_ids:
            logger.warning("No ReccoBeats IDs found for audio features")
            return tracks  # Return original tracks if no audio features available

        # Get audio features using repo with callback
        audio_features_map = await self.playlist_repo.get_or_fetch_reccobeats_audio_features(
            reccobeats_ids=reccobeats_ids,
            fetch_callback=lambda: self.reccobeats_client.fetch_audio_features_batch(
                reccobeats_ids
            ),
        )

        # Filter based on vibe
        filtered_tracks = []
        for track in tracks:
            track_id = track.get("id")
            if not track_id or track_id not in reccobeats_metadata:
                continue

            reccobeats_id = reccobeats_metadata[track_id].get("reccobeats_id")
            if not reccobeats_id:
                continue

            audio_features = audio_features_map.get(reccobeats_id, {})

            if self._track_matches_vibe(audio_features, vibe):
                # Add audio features to track data
                track["audio_features"] = audio_features
                filtered_tracks.append(track)

        return filtered_tracks

    def _track_matches_vibe(self, audio_features: dict[str, Any], vibe: str) -> bool:
        """Check if a track's audio features match the desired vibe."""
        if not audio_features:
            return True  # Include tracks without features rather than exclude them

        energy = audio_features.get("energy")
        valence = audio_features.get("valence")
        tempo = audio_features.get("tempo")

        if vibe.lower() == "chill":
            # Chill tracks: lower energy, moderate valence, slower tempo
            return (energy is None or energy < 0.6) and (tempo is None or tempo < 120)
        elif vibe.lower() == "upbeat":
            # Upbeat tracks: higher energy, higher valence, faster tempo
            return (
                (energy is None or energy > 0.5)
                and (valence is None or valence > 0.4)
                and (tempo is None or tempo > 100)
            )

        # Default: include the track
        return True

    def _select_tracks_for_duration(
        self, tracks: list[dict[str, Any]], target_minutes: int
    ) -> list[dict[str, Any]]:
        """Select tracks to approximately match the target duration."""
        if not tracks:
            return []

        target_ms = target_minutes * 60 * 1000
        selected_tracks = []
        total_duration = 0

        # Shuffle for variety
        shuffled_tracks = tracks.copy()
        random.shuffle(shuffled_tracks)

        for track in shuffled_tracks:
            track_duration = track.get("duration_ms", 0)

            if total_duration + track_duration <= target_ms * 1.2:  # 20% buffer
                selected_tracks.append(track)
                total_duration += track_duration

                if total_duration >= target_ms * 0.9:  # At least 90% of target
                    break

        return selected_tracks

    def _format_tracks_for_response(
        self, tracks: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Format tracks for the API response."""
        formatted_tracks = []

        for track in tracks:
            track_id = track.get("id")
            track_name = track.get("name")

            # Get artist name
            artist_name = "Unknown Artist"
            if (
                track.get("artists")
                and isinstance(track["artists"], list)
                and len(track["artists"]) > 0
            ):
                artist_name = track["artists"][0].get("name", "Unknown Artist")

            spotify_url = track.get("external_urls", {}).get("spotify")
            preview_url = track.get("preview_url")
            duration_ms = track.get("duration_ms")

            # Get album info
            album_data = track.get("album", {})

            # Ensure we have essential data
            if all(
                [
                    track_name,
                    artist_name != "Unknown Artist",
                    spotify_url,
                    duration_ms is not None,
                ]
            ):
                formatted_tracks.append(
                    {
                        "id": track_id,
                        "name": track_name,
                        "artist": artist_name,
                        "album": album_data,  # Keep full album object
                        "duration": duration_ms,
                        "spotifyUrl": spotify_url,
                        "previewUrl": preview_url,
                    }
                )
            else:
                logger.debug(f"Skipping track due to missing data: {track_name}")

        return formatted_tracks

    def _create_spotify_playlist(
        self,
        activity: str,
        vibe: str,
        tracks: list[dict[str, Any]],
        duration_minutes: int,
    ) -> dict[str, Any] | None:
        """Create the actual Spotify playlist."""
        try:
            playlist_name = f"{vibe.capitalize()} {activity.capitalize()}"
            playlist_description = f"A {vibe} playlist for your {activity} session, approximately {duration_minutes} minutes long."

            # Create playlist
            playlist = self.spotify_client.create_playlist(
                name=playlist_name, description=playlist_description, public=True
            )

            if not playlist:
                return None

            # Add tracks
            track_uris = [track["spotifyUrl"] for track in tracks]
            success = self.spotify_client.add_tracks_to_playlist(
                playlist["id"], track_uris
            )

            if not success:
                logger.error("Failed to add tracks to playlist")
                return None

            # Try to upload cover image
            default_cover_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "..",
                "..",
                "default_playlist_cover.jpg",
            )

            image_url = None
            if os.path.exists(default_cover_path):
                if self.spotify_client.upload_playlist_cover(
                    playlist["id"], default_cover_path
                ):
                    # Get updated playlist to retrieve image URL
                    updated_playlist = self.spotify_client.get_playlist(playlist["id"])
                    if updated_playlist and updated_playlist.get("images"):
                        image_url = updated_playlist["images"][0].get("url")

            return {
                "playlist_id": playlist["id"],
                "playlist_url": playlist["external_urls"]["spotify"],
                "playlist_name": playlist["name"],
                "playlist_description": playlist["description"],
                "playlist_image_url": image_url
                or "https://via.placeholder.com/300x300.png?text=Playlist+Image",
            }

        except Exception as e:
            logger.error(f"Error creating Spotify playlist: {e}")
            return None

    async def get_playlist_by_id(self, playlist_id: str) -> dict[str, Any] | None:
        """
        Get a playlist by its ID from cache.

        Args:
            playlist_id: The playlist ID to retrieve

        Returns:
            Playlist data if found, None otherwise
        """
        return await self.playlist_repo.get_playlist_by_id(playlist_id)
