import asyncio
import os
from unittest.mock import MagicMock, AsyncMock

import pytest
from app.integrations.gemini import GeminiClient
from app.playlists.service import PlaylistService


@pytest.fixture
def mock_spotify_client():
    client = MagicMock()
    client.create_playlist.return_value = {
        "id": "test_playlist_id",
        "external_urls": {"spotify": "https://open.spotify.com/playlist/test_playlist_id"},
        "name": "Test Playlist",
        "description": "A test playlist.",
    }
    client.add_tracks_to_playlist.return_value = True
    client.upload_playlist_cover_image_data.return_value = True
    client.get_playlist.return_value = {
        "images": [{"url": "http://example.com/image.jpg"}]
    }
    return client


@pytest.fixture
def mock_reccobeats_client():
    return MagicMock()


@pytest.fixture
def mock_playlist_repo():
    repo = MagicMock()
    repo.get_generated_playlist.return_value = None
    repo.get_or_fetch_spotify_tracks.return_value = [
        {
            "id": "test_track_id",
            "name": "Test Track",
            "artists": [{"name": "Test Artist"}],
            "duration_ms": 180000,
            "external_urls": {"spotify": "https://open.spotify.com/track/test_track_id"},
            "preview_url": "http://example.com/preview.mp3",
            "album": {},
        }
    ]
    repo.get_or_fetch_reccobeats_metadata.return_value = {}
    repo.get_or_fetch_reccobeats_audio_features.return_value = {}
    return repo


@pytest.fixture
def gemini_client():
    return GeminiClient()


@pytest.mark.asyncio
async def test_playlist_creation_with_image_generation(
    mock_spotify_client,
    mock_reccobeats_client,
    mock_playlist_repo,
    gemini_client,
):
    # Arrange
    playlist_service = PlaylistService(
        spotify_client=mock_spotify_client,
        reccobeats_client=mock_reccobeats_client,
        playlist_repo=mock_playlist_repo,
        gemini_client=gemini_client,
    )
    mock_spotify_client.is_connected.return_value = True

    # Act
    playlist = await playlist_service.create_activity_playlist(
        activity="coding", vibe="chill", duration_minutes=30
    )

    # Assert
    assert playlist is not None
    assert playlist["name"] == "Chill Coding"
    assert "http://example.com/image.jpg" in playlist["imageUrl"]
    mock_spotify_client.create_playlist.assert_called_once()
    mock_spotify_client.add_tracks_to_playlist.assert_called_once()
    gemini_client.generate_playlist_image.assert_called_once()
    mock_spotify_client.upload_playlist_cover_image_data.assert_called_once()
