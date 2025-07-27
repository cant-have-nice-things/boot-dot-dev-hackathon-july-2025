import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException
from dotenv import load_dotenv # Make sure to install python-dotenv: pip install python-dotenv

load_dotenv() # Load environment variables from .env file

client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")
SCOPE = "playlist-modify-public"

print(f"Testing Spotify Client ID: {client_id}")
print(f"Testing Spotify Client Secret (first 5 chars): {client_secret[:5]}")
print(f"Testing Spotify Redirect URI {redirect_uri}...")

if not client_id or not client_secret or not redirect_uri:
    print("Error: Spotify client ID or secret not found in environment variables.")
else:
    try:
        auth_manager = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=SCOPE
        )
        sp = spotipy.Spotify(auth_manager=auth_manager)

        access_token = auth_manager.get_access_token()

        sp = spotipy.Spotify(auth=access_token)
        user_id = sp.current_user()['id']
        print(user_id)

        # Create the playlist
        playlist_name = "My New Automated Playlist"
        playlist_description = "Created via Spotify API with OAuth2"
        new_playlist = sp.user_playlist_create(
            user=user_id,
            name=playlist_name,
            public=True,  # Set to False for a private playlist
            description=playlist_description
        )

        print(f"Playlist '{new_playlist['name']}' created with ID: {new_playlist['id']}")

    except SpotifyException as e:
        print(f"Spotify API Error in standalone script: Status {e.http_status}, Code {e.code}, Message: {e.msg}")
    except Exception as e:
        print(f"An unexpected error occurred in standalone script: {e}")
