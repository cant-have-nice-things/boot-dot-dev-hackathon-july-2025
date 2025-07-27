from typing import Any

from pydantic import BaseModel, Field


class PlaylistRequest(BaseModel):
    """Request model for playlist generation."""

    activity: str = Field(
        ..., description="The activity (e.g., yoga, studying, cleaning)"
    )
    vibe: str = Field(..., description="The vibe (e.g., chill, upbeat)")
    duration: int = Field(30, ge=5, le=120, description="Playlist duration in minutes")


class Track(BaseModel):
    """Track model for API responses."""

    id: str
    name: str
    artist: str
    album: dict[str, Any]  # Contains name and images
    duration: int  # Duration in milliseconds
    spotifyUrl: str
    previewUrl: str | None = None


class PlaylistResponse(BaseModel):
    """Response model for generated playlists."""

    id: str
    name: str
    description: str
    spotifyUrl: str
    imageUrl: str
    tracks: list[Track]
    duration: int  # Total playlist duration in minutes
    createdAt: str
