# backend/app/routes/playlist.py
import time
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..services.spotify_service import create_activity_playlist

router = APIRouter()

class PlaylistRequest(BaseModel):
    activity: str
    duration: int
    vibe: str

class Track(BaseModel):
    id: str
    name: str
    artist: str
    album: str # Frontend expects this. Added explicitly here for Pydantic model
    duration: int # Duration in milliseconds
    spotifyUrl: str
    previewUrl: str | None = None

class PlaylistResponse(BaseModel):
    id: str
    name: str
    description: str
    spotifyUrl: str
    # Add imageUrl for playlist cover
    imageUrl: str # New field for playlist cover image URL
    tracks: list[Track]
    duration: int # Total playlist duration in minutes
    createdAt: str


@router.post("/generate-playlist", response_model=PlaylistResponse)
async def generate_playlist(request: PlaylistRequest):
    print("Received request for playlist generation from frontend.")
    
    playlist_data_from_service = create_activity_playlist(
        activity=request.activity,
        vibe=request.vibe,
        duration=request.duration
    )

    if "error" in playlist_data_from_service:
        print(f"Error from playlist generation service: {playlist_data_from_service['error']}")
        raise HTTPException(status_code=404, detail=playlist_data_from_service["error"])

    # Extract data from the service's result (which now contains real Spotify playlist details)
    generated_tracks_raw = playlist_data_from_service.get("tracks", [])
    total_playlist_duration_minutes = playlist_data_from_service.get("total_duration_minutes", 0)
    
    # Get actual Spotify playlist details
    actual_playlist_id = playlist_data_from_service.get("playlist_id")
    actual_playlist_name = playlist_data_from_service.get("playlist_name")
    actual_playlist_description = playlist_data_from_service.get("playlist_description")
    actual_spotify_url = playlist_data_from_service.get("playlist_url")
    actual_playlist_image_url = playlist_data_from_service.get("playlist_image_url")


    formatted_tracks: list[Track] = []
    for track_raw in generated_tracks_raw:
        # Ensure album field is populated for frontend
        album_name = track_raw.get("album", {}).get("name", "Unknown Album")
        # Ensure 'images' list is handled correctly for album cover
        album_images = track_raw.get("album", {}).get("images", [])
        album_image_url = album_images[0].get('url') if album_images and len(album_images) > 0 else None

        formatted_tracks.append(
            Track(
                id=track_raw.get("id", "unknown_id"),
                name=track_raw.get("name", "Unknown Track"),
                artist=track_raw.get("artist", "Unknown Artist"),
                album=album_name, # Pass album name
                duration=track_raw.get("duration", 0), # Ensure this is in milliseconds as per Track model
                spotifyUrl=track_raw.get("spotifyUrl", "http://googleusercontent.com/invalid_spotify_url"),
                previewUrl=track_raw.get("previewUrl")
            )
        )

    timestamp = int(time.time() * 1000)

    # Create the response using actual generated data
    response = PlaylistResponse(
        id=actual_playlist_id or f"generated_playlist_{timestamp}",
        name=actual_playlist_name or f"{request.activity} - {request.vibe} Playlist",
        description=actual_playlist_description or f"A {request.vibe} playlist for your {request.activity} session.",
        spotifyUrl=actual_spotify_url or f"http://googleusercontent.com/mock-spotify-playlist-url-{timestamp}",
        imageUrl=actual_playlist_image_url or "https://via.placeholder.com/300x300.png?text=Playlist+Image", # Use actual or default
        duration=int(total_playlist_duration_minutes),
        createdAt=datetime.now().isoformat(),
        tracks=formatted_tracks,
    )

    print(f"Successfully generated playlist response with {len(formatted_tracks)} tracks.")
    return response
