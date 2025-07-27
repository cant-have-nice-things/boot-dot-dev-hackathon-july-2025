import time
from datetime import datetime
from fastapi import APIRouter, HTTPException # Import HTTPException for proper error handling
from pydantic import BaseModel, Field # Import Field if using it for validation

# Import the create_activity_playlist function from your spotify_service
from ..services.spotify_service import create_activity_playlist

router = APIRouter()

# Define the Pydantic models for request and response as expected by frontend
class PlaylistRequest(BaseModel):
    activity: str
    duration: int
    vibe: str


class Track(BaseModel):
    id: str
    name: str
    artist: str
    album: str # Frontend expects this. Ensure it's handled or mocked from backend
    duration: int # Duration in milliseconds
    spotifyUrl: str
    previewUrl: str | None = None


class PlaylistResponse(BaseModel):
    id: str
    name: str
    description: str
    spotifyUrl: str
    tracks: list[Track]
    duration: int # Total playlist duration in minutes
    createdAt: str


@router.post("/generate-playlist", response_model=PlaylistResponse)
async def generate_playlist(request: PlaylistRequest):
    print("Received request for playlist generation from frontend.")
    
    # Call the actual playlist generation logic from spotify_service.py
    # This will return the filtered tracks and metadata
    playlist_data = create_activity_playlist(
        activity=request.activity,
        vibe=request.vibe,
        duration=request.duration
    )

    if "error" in playlist_data:
        print(f"Error from playlist generation service: {playlist_data['error']}")
        # Return a 404 Not Found if no suitable tracks are found
        raise HTTPException(status_code=404, detail=playlist_data["error"])

    # Extract the tracks and total duration from the service response
    generated_tracks_raw = playlist_data.get("tracks", [])
    total_playlist_duration_minutes = playlist_data.get("total_duration_minutes", 0)
    # The 'criteria' field is not part of the frontend's PlaylistResponse, so we don't include it here.


    # Convert the raw track data into the PlaylistResponse.Track format
    formatted_tracks: list[Track] = []
    for track_raw in generated_tracks_raw:
        # Spotify search results typically have 'album' data under 'album.name'
        # ReccoBeats metadata from /v1/track might also have album info.
        # If not, you might need to adjust spotify_service.py to include it, or mock it here.
        album_name = track_raw.get("album", {}).get("name", "Unknown Album") # Safely get album name
        
        formatted_tracks.append(
            Track(
                id=track_raw.get("id", "unknown_id"),
                name=track_raw.get("name", "Unknown Track"),
                artist=track_raw.get("artist", "Unknown Artist"),
                album=album_name, # Use the safely extracted album name
                duration=track_raw.get("duration_ms", 0), # Ensure this is in milliseconds
                spotifyUrl=track_raw.get("spotify_url", "http://googleusercontent.com/invalid_spotify_url"),
                previewUrl=track_raw.get("preview_url")
            )
        )

    # Generate timestamp for unique ID for the response playlist
    timestamp = int(time.time() * 1000)

    # Create the actual response using the generated data
    response = PlaylistResponse(
        id=f"generated_playlist_{timestamp}", # Unique ID for this generated playlist response
        name=f"{request.activity} - {request.vibe} Playlist", # Dynamic name
        description=f"A {request.vibe} playlist for your {request.activity} session, approximately {int(total_playlist_duration_minutes)} minutes long.", # Dynamic description
        spotifyUrl=f"http://googleusercontent.com/mock-spotify-playlist-url-{timestamp}", # Mock URL, as real creation is complex for hackathon
        duration=int(total_playlist_duration_minutes),
        createdAt=datetime.now().isoformat(),
        tracks=formatted_tracks,
    )

    print(f"Successfully generated playlist response with {len(formatted_tracks)} tracks.")
    return response
