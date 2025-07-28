import os

from pydantic import BaseModel


class SpotifyConfig(BaseModel):
    """Spotify API configuration."""

    client_id: str
    client_secret: str
    redirect_uri: str = "http://localhost:8000/callback"
    cache_path: str = ".spotipy_cache.json"
    scopes: str = "playlist-modify-public ugc-image-upload user-read-private"

    @classmethod
    def from_env(cls) -> "SpotifyConfig":
        """Create configuration from environment variables."""
        client_id = os.getenv("SPOTIFY_CLIENT_ID")
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

        if not client_id or not client_secret:
            raise ValueError(
                "SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be set in environment variables"
            )

        return cls(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=os.getenv(
                "SPOTIFY_REDIRECT_URI", "http://localhost:8000/callback"
            ),
            cache_path=os.getenv("SPOTIPY_CACHE_PATH", ".spotipy_cache.json"),
            scopes=os.getenv(
                "SPOTIFY_SCOPES",
                "playlist-modify-public ugc-image-upload user-read-private",
            ),
        )
