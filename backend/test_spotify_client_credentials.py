import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.exceptions import SpotifyException
from dotenv import load_dotenv # Make sure to install python-dotenv: pip install python-dotenv

load_dotenv() # Load environment variables from .env file

client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

print(f"Testing Spotify Client ID: {client_id}")
print(f"Testing Spotify Client Secret (first 5 chars): {client_secret[:5]}...")

if not client_id or not client_secret:
    print("Error: Spotify client ID or secret not found in environment variables.")
else:
    try:
        client_credentials_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        sp = spotipy.Spotify(auth_manager=client_credentials_manager)
#        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

        playlists = sp.user_playlists('spotify')
        while playlists:
            for i, playlist in enumerate(playlists['items']):
                print(f"{i + 1 + playlists['offset']:4d} {playlist['uri']} {playlist['name']}")
            if playlists['next']:
                playlists = sp.next(playlists)
            else:
                playlists = None


        # Use some known track IDs for testing
#        test_track_ids = ['7GF382gqL7SgN0F0XgA5Jb', '2P8hRKo1E5q9DnmzKbdw00', '1RAT5CmXzvhgS5sl37FHa6'] # Example IDs

#        print(f"Attempting to fetch audio features for: {test_track_ids}")
#        audio_features = sp.audio_features(test_track_ids)
#        print("Successfully fetched audio features in standalone script:")
#        for feature in audio_features:
#            if feature:
#                print(f"  Track ID: {feature['id']}, Tempo: {feature['tempo']}, Energy: {feature['energy']}")
#            else:
#                print("  Could not retrieve features for a track.")

    except SpotifyException as e:
        print(f"Spotify API Error in standalone script: Status {e.http_status}, Code {e.code}, Message: {e.msg}")
    except Exception as e:
        print(f"An unexpected error occurred in standalone script: {e}")
