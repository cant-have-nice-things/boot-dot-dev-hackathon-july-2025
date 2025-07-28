import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

def main():
    """
    This script will guide you through the Spotify authentication process.
    It will create a .spotipy_cache file in the root of the project.
    """
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8000/callback")
    scopes = os.getenv(
        "SPOTIFY_SCOPES",
        "playlist-modify-public ugc-image-upload user-read-private",
    )

    if not client_id or not client_secret:
        print("Please set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in your .env file.")
        return

    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=scopes,
        cache_path=".spotipy_cache.json",
        show_dialog=True,
    )

    sp = spotipy.Spotify(auth_manager=auth_manager)

    # Make a request to the Spotify API to trigger the authentication flow
    try:
        user = sp.current_user()
        print(f"Successfully authenticated as {user['display_name']}")
        print("A .spotipy_cache.json file has been created in the root of the project.")
        print("Please move this file to the backend directory and rename it to .spotipy_cache")

    except Exception as e:
        print(f"An error occurred during authentication: {e}")


if __name__ == "__main__":
    main()
