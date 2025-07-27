import logging

from fastapi import APIRouter, HTTPException

from ..dependencies import PlaylistServiceDep, SpotifyClientDep
from ..playlists import PlaylistRequest, PlaylistResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/generate-playlist", response_model=PlaylistResponse)
async def generate_playlist(
        request: PlaylistRequest,
        playlist_service: PlaylistServiceDep,
        spotify_client: SpotifyClientDep,
):
    """
    Generate a Spotify playlist based on activity, vibe, and duration.
    """
    logger.info(
        f"Received playlist request: {request.activity}, {request.vibe}, {request.duration}min"
    )

    # Ensure Spotify client is connected
    if not spotify_client.is_connected():
        connected = await spotify_client.connect()
        if not connected:
            raise HTTPException(
                status_code=503,
                detail="Spotify service unavailable. Please check authentication.",
            )

    try:
        # Generate playlist using the service - service handles all the logic and formatting
        playlist_data = await playlist_service.create_activity_playlist(
            activity=request.activity,
            vibe=request.vibe,
            duration_minutes=request.duration,
        )

        # Check for errors from service
        if "error" in playlist_data:
            logger.error(f"Playlist generation error: {playlist_data['error']}")
            raise HTTPException(status_code=404, detail=playlist_data["error"])

        # Service returns data in the exact format needed for the response
        logger.info(
            f"Successfully generated playlist with {len(playlist_data.get('tracks', []))} tracks"
        )
        return PlaylistResponse(**playlist_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error generating playlist: {e}")
        raise HTTPException(
            status_code=500, detail="Internal server error while generating playlist"
        ) from e


@router.get("/playlist/{playlist_id}", response_model=PlaylistResponse)
async def get_playlist_by_id(
        playlist_id: str,
        playlist_service: PlaylistServiceDep,
):
    """
    Get a playlist by its ID from cache.
    """
    logger.info(f"Received request for playlist ID: {playlist_id}")

    try:
        # Try to get playlist from cache by ID
        playlist_data = await playlist_service.get_playlist_by_id(playlist_id)

        if not playlist_data:
            logger.warning(f"Playlist not found: {playlist_id}")
            raise HTTPException(
                status_code=404,
                detail=f"Playlist with ID {playlist_id} not found"
            )

        logger.info(f"Successfully retrieved playlist: {playlist_id}")
        return PlaylistResponse(**playlist_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error retrieving playlist {playlist_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving playlist"
        ) from e


@router.get("/health")
async def playlist_health(spotify_client: SpotifyClientDep):
    """Health check for playlist service."""
    try:
        if not spotify_client.is_connected():
            connected = await spotify_client.connect()
            if not connected:
                return {"status": "unhealthy", "spotify": "disconnected"}

        # Simple test search
        test_tracks = spotify_client.search_tracks("test", limit=1)

        return {
            "status": "healthy",
            "spotify": "connected",
            "test_search": len(test_tracks) > 0,
        }
    except Exception as e:
        logger.error(f"Playlist health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}