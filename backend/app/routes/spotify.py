# backend/app/routes/spotify.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from app.services.spotify_service import SpotifyService, create_activity_playlist

router = APIRouter()
#router = APIRouter(prefix="/spotify", tags=["spotify"])

class PlaylistRequest(BaseModel):
    activity: str = Field(..., description="The activity (e.g., yoga, studying, cleaning)")
    vibe: str = Field(..., description="The vibe (chill, upbeat)")
    duration: int = Field(30, ge=5, le=120, description="Playlist duration in minutes")

class Track(BaseModel):
    name: str
    artist: str
    spotify_url: str
    preview_url: Optional[str]
    duration_ms: int

class PlaylistResponse(BaseModel):
    tracks: List[Track]
    total_duration_minutes: float
    criteria: Dict[str, Any]
    error: Optional[str] = None

@router.post("/generate-playlist", response_model=PlaylistResponse)
async def generate_playlist(request: PlaylistRequest):
    """
    Generate a Spotify playlist based on activity and vibe.
    
    This endpoint searches for tracks that match the user's criteria
    and returns a curated list without requiring user authentication.
    """
    print("Trying to create_activity_playlist")

    try:
        result = create_activity_playlist(
            activity=request.activity,
            vibe=request.vibe,
            duration=request.duration
        )
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return PlaylistResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error generating playlist: {str(e)}"
        )

@router.get("/search-preview")
async def search_preview(activity: str, vibe: str, limit: int = 10):
    """
    Preview tracks for given criteria without full playlist generation.
    Useful for testing or showing quick results.
    """
    try:
        spotify_service = SpotifyService()
        tracks = spotify_service.search_tracks_by_criteria(
            activity=activity,
            vibe=vibe,
            duration_minutes=10,  # Short duration for preview
            limit=limit
        )
        
        if not tracks:
            return {"message": "No tracks found for these criteria"}
        
        return {
            "preview_tracks": [
                {
                    "name": track['name'],
                    "artist": track['artists'][0]['name'],
                    "spotify_url": track['external_urls']['spotify'],
                    "tempo": track.get('audio_features', {}).get('tempo', 'Unknown'),
                    "energy": track.get('audio_features', {}).get('energy', 'Unknown')
                }
                for track in tracks[:limit]
            ],
            "total_found": len(tracks)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching tracks: {str(e)}"
        )

# Add health check endpoint
@router.get("/health")
async def spotify_health():
    """Check if Spotify service is working."""
    try:
        spotify_service = SpotifyService()
        # Simple test search
        result = spotify_service.sp.search(q="test", type="track", limit=1)
        return {"status": "healthy", "spotify_api": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
