import time
from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class PlaylistRequest(BaseModel):
    activity: str
    duration: int
    vibe: str


class Track(BaseModel):
    id: str
    name: str
    artist: str
    album: str
    duration: int
    spotifyUrl: str
    previewUrl: str | None = None


class PlaylistResponse(BaseModel):
    id: str
    name: str
    description: str
    spotifyUrl: str
    tracks: list[Track]
    duration: int
    createdAt: str


@router.post("/generate-playlist", response_model=PlaylistResponse)
async def generate_playlist(request: PlaylistRequest):
    # TODO: Implement actual playlist generation logic
    # For now, return the same mock data structure
    # Generate timestamp for unique ID
    timestamp = int(time.time() * 1000)  # JavaScript Date.now() equivalent

    # Create mock tracks
    mock_tracks = [
        Track(
            id="track1",
            name="Sample Song 1",
            artist="Sample Artist",
            album="Sample Album",
            duration=210,
            spotifyUrl="https://open.spotify.com/track/mock1",
            previewUrl="https://example.com/preview1.mp3",
        ),
        Track(
            id="track2",
            name="Sample Song 2",
            artist="Another Artist",
            album="Another Album",
            duration=195,
            spotifyUrl="https://open.spotify.com/track/mock2",
        ),
    ]

    # Create the response
    response = PlaylistResponse(
        id=f"playlist_{timestamp}",
        name=f"{request.activity} Vibes",
        description=f"A {request.vibe} playlist for {request.activity} ({request.duration} minutes)",
        spotifyUrl="https://open.spotify.com/playlist/mock",
        duration=request.duration,
        createdAt=datetime.now().isoformat(),
        tracks=mock_tracks,
    )

    return response
