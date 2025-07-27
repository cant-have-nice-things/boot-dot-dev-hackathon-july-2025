# backend/app/services/spotify_service.py

import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from typing import List, Dict, Any, Optional
import random
import http.client
import json
import urllib.parse
import base64

_reccobeats_final_audio_features_cache = {}

class SpotifyService:
    def __init__(self):
        """
        Initializes Spotify client using OAuth for user-specific actions (playlist creation)
        and handles ReccoBeats API calls.
        """
        client_id = os.getenv("SPOTIFY_CLIENT_ID")
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")
        cache_path = os.getenv("SPOTIPY_CACHE_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".spotipy_cache.json"))

        scopes = "playlist-modify-public ugc-image-upload user-read-private"

        if not all([client_id, client_secret, redirect_uri]):
            print("ERROR: SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, or SPOTIPY_REDIRECT_URI not set in .env.")
            print("OAuth operations (like playlist creation) will not be available.")
            self.sp = None
            self.user_id = None
            raise ValueError("Missing Spotify API credentials for OAuth. Please check your .env file.")
        
        self.auth_manager = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=scopes,
            cache_path=cache_path,
        )
        
        self.sp = spotipy.Spotify(auth_manager=self.auth_manager)
        self.user_id = None

        try:
            current_user_profile = self.sp.current_user()
            self.user_id = current_user_profile['id']
            print(f"Successfully authenticated SpotifyService as user: {self.user_id}")
        except Exception as e:
            print(f"\n\n*** IMPORTANT: Spotify OAuth authentication failed or token not found/expired. ***")
            print(f"Error: {e}")
            print(f"Please run `python backend/test_spotify_auth_credentials.py` once to authenticate your Spotify account and get the initial token.")
            print(f"Make sure SPOTIPY_CACHE_PATH is set correctly in your .env file (e.g., {cache_path}).")
            print("*** Playlist creation will fail until authentication is complete. ***\n")
            self.sp = None

    def _fetch_reccobeats_metadata_batch(self, spotify_ids: List[str]) -> Dict[str, Any]:
        """
        Fetches basic track metadata from ReccoBeats API for a batch of Spotify IDs.
        Returns a dictionary mapping original Spotify ID to its ReccoBeats ID and metadata.
        """
        spotify_to_reccobeats_map = {}
        print(f"Attempting to fetch ReccoBeats metadata for {len(spotify_ids)} Spotify IDs.")

        RECCOBEATS_BATCH_LIMIT = 40
        for i in range(0, len(spotify_ids), RECCOBEATS_BATCH_LIMIT):
            batch_spotify_ids = spotify_ids[i:i + RECCOBEATS_BATCH_LIMIT]
            if not batch_spotify_ids:
                continue

            ids_string = ",".join(batch_spotify_ids)
            query_params = urllib.parse.urlencode({'ids': ids_string})
            full_path = f"/v1/track?{query_params}"

            conn = http.client.HTTPSConnection("api.reccobeats.com")
            headers = {
              'Accept': 'application/json'
            }
            try:
                conn.request("GET", full_path, '', headers)
                res = conn.getresponse()
                data = res.read().decode("utf-8")

                if res.status == 200:
                    response_json = json.loads(data)
                    if isinstance(response_json, dict) and 'content' in response_json and isinstance(response_json['content'], list):
                        for track_metadata in response_json['content']:
                            reccobeats_id = track_metadata.get('id')
                            spotify_url_from_reccobeats = track_metadata.get('href')

                            if reccobeats_id and spotify_url_from_reccobeats:
                                parsed_url = urllib.parse.urlparse(spotify_url_from_reccobeats)
                                path_segments = parsed_url.path.split('/')
                                actual_spotify_id = path_segments[-1] if path_segments else None

                                if actual_spotify_id:
                                    spotify_to_reccobeats_map[actual_spotify_id] = {
                                        "reccobeats_id": reccobeats_id,
                                        "metadata": track_metadata
                                    }
                                else:
                                    print(f"Warning: Could not parse Spotify ID from href '{spotify_url_from_reccobeats}' in metadata batch.")
                            else:
                                print(f"Warning: ReccoBeats metadata missing 'id' or 'href' for a track in batch {batch_spotify_ids}.")
                    else:
                        print(f"ReccoBeats API Error: Unexpected response format for metadata batch {batch_ids}. Response: {data}")
                else:
                    print(f"ReccoBeats API Error for metadata batch {batch_ids}: Status {res.status}, Response: {data}")
            except json.JSONDecodeError as e:
                print(f"JSON Decode Error for metadata batch {batch_ids}: {e}, Raw response: {data}")
            except Exception as e:
                print(f"Error connecting to ReccoBeats API for metadata batch {batch_ids}: {str(e)}")
            finally:
                conn.close()
        print(f"Successfully mapped {len(spotify_to_reccobeats_map)} Spotify IDs to ReccoBeats info.")
        return spotify_to_reccobeats_map


    def _fetch_reccobeats_audio_features_single(self, reccobeats_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetches audio features for a single ReccoBeats ID from ReccoBeats API.
        """
        if reccobeats_id in _reccobeats_final_audio_features_cache:
            return _reccobeats_final_audio_features_cache[reccobeats_id]

        conn = http.client.HTTPSConnection("api.reccobeats.com")
        headers = {
          'Accept': 'application/json'
        }
        try:
            full_path = f"/v1/track/{reccobeats_id}/audio-features"
            conn.request("GET", full_path, '', headers)
            res = conn.getresponse()
            data = res.read().decode("utf-8")
            
            if res.status == 200:
                response_json = json.loads(data)
                if isinstance(response_json, dict):
                    _reccobeats_final_audio_features_cache[reccobeats_id] = response_json 
                    return response_json
                else:
                    print(f"ReccoBeats Audio Features API Error: Expected dict, got {type(response_json).__name__} for ReccoBeats ID {reccobeats_id}. Response: {data}")
                    return None
            else:
                print(f"ReccoBeats Audio Features API Error for ReccoBeats ID {reccobeats_id}: Status {res.status}, Response: {data}")
                return None
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error for audio features ReccoBeats ID {reccobeats_id}: {e}, Raw response: {data}")
            return None
        except Exception as e:
            print(f"Error connecting to ReccoBeats Audio Features API for ReccoBeats ID {reccobeats_id}: {str(e)}")
            return None
        finally:
            conn.close()

    def search_tracks_by_criteria(
        self,
        activity: str,
        vibe: str,
        duration_minutes: int = 30,
        # Increased initial limit to fetch more tracks for better filtering
        total_fetch_limit: int = 200 # New parameter for total tracks to fetch
    ) -> List[Dict[str, Any]]:
        """
        Search for tracks based on activity and vibe.
        Fetches multiple batches of tracks from Spotify.
        """
        search_params = self._convert_to_search_params(activity, vibe)
        query = self._build_search_query(activity, search_params)

        all_tracks = []
        offset = 0
        spotify_api_limit = 50 # Max limit per Spotify API search request

        print(f"Spotify search query: '{query}', attempting to fetch up to {total_fetch_limit} tracks.") # New log
        while offset < total_fetch_limit:
            results = self.sp.search(
                q=query,
                type='track',
                limit=spotify_api_limit,
                offset=offset,
                market='US'
            )
            tracks_batch = results['tracks']['items']
            if not tracks_batch:
                break # No more tracks to fetch

            all_tracks.extend(tracks_batch)
            offset += spotify_api_limit

            if len(all_tracks) >= total_fetch_limit:
                break # Reached desired total limit

        print(f"Spotify search returned {len(all_tracks)} total tracks across all requests.") # Modified log
        tracks_to_filter = all_tracks[:total_fetch_limit] # Ensure we don't process more than needed

        filtered_tracks = self._filter_by_audio_features(tracks_to_filter, search_params)
        print(f"After audio features filtering, {len(filtered_tracks)} tracks remain.")

        selected_tracks = self._select_tracks_for_duration(
            filtered_tracks,
            duration_minutes
        )
        print(f"After duration selection, {len(selected_tracks)} tracks remain.")
        
        # New: Sort tracks for energy progression
        final_sorted_tracks = self._sort_tracks_by_energy_progression(selected_tracks)
        print(f"Final playlist has {len(final_sorted_tracks)} tracks after sorting by energy progression.")
        return final_sorted_tracks

    def _convert_to_search_params(self, activity: str, vibe: str) -> Dict[str, Any]:
        """Convert user input to Spotify audio feature parameters."""
        vibe_mappings = {
            "chill": {
                "tempo_range": (60, 100), "energy_range": (0.1, 0.6), "valence_range": (0.2, 0.8), "danceability_range": (0.2, 0.7)
            },
            "upbeat": {
                "tempo_range": (110, 180), "energy_range": (0.6, 1.0), "valence_range": (0.5, 1.0), "danceability_range": (0.5, 1.0)
            },
            "pop dance": {
                "tempo_range": (115, 160),
                "energy_range": (0.6, 1.0),
                "valence_range": (0.7, 1.0),
                "danceability_range": (0.7, 1.0)
            },
            "dance": {
                "tempo_range": (115, 160),
                "energy_range": (0.6, 1.0),
                "valence_range": (0.7, 1.0),
                "danceability_range": (0.7, 1.0)
            },
            "dance pop": {
                "tempo_range": (115, 160),
                "energy_range": (0.6, 1.0),
                "valence_range": (0.7, 1.0),
                "danceability_range": (0.7, 1.0)
            }
        }
        activity_mappings = {
            "yoga": {
                "keywords": ["ambient", "meditation", "peaceful", "zen"], "tempo_adjustment": -10, "energy_adjustment": -0.2
            },
            "studying": {
                "keywords": ["focus", "instrumental", "ambient", "lo-fi"], "tempo_adjustment": 0, "energy_adjustment": -0.3
            },
            "cleaning": {
                "keywords": ["energetic", "pop", "dance"], "tempo_adjustment": +15, "energy_adjustment": +0.1
            },
            "workout": {
                "keywords": ["pump up", "energetic", "motivation"], "tempo_adjustment": +20, "energy_adjustment": +0.2
            },
            "cooking": {
                "keywords": ["uplifting", "feel good", "positive"], "tempo_adjustment": +5, "energy_adjustment": 0
            }
        }
        base_params = vibe_mappings.get(vibe.lower(), vibe_mappings["chill"])
        activity_config = activity_mappings.get(
            activity.lower(),
            {"keywords": [], "tempo_adjustment": 0, "energy_adjustment": 0}
        )
        tempo_min, tempo_max = base_params["tempo_range"]
        tempo_adj = activity_config["tempo_adjustment"]
        energy_min, energy_max = base_params["energy_range"]
        energy_adj = activity_config["energy_adjustment"]
        return {
            "keywords": activity_config["keywords"],
            "tempo_range": (
                max(50, tempo_min + tempo_adj),
                min(200, tempo_max + tempo_adj)
            ),
            "energy_range": (
                max(0.0, energy_min + energy_adj),
                min(1.0, energy_max + energy_adj)
            ),
            "valence_range": base_params["valence_range"],
            "danceability_range": base_params["danceability_range"]
        }

    def _build_search_query(self, activity: str, params: Dict[str, Any]) -> str:
        """Build Spotify search query string."""
        query_parts = []
        query_parts.append(activity)
        if params["keywords"]:
            selected_keywords = random.sample(
                params["keywords"],
                min(2, len(params["keywords"]))
            )
            query_parts.extend(selected_keywords)
        return " ".join(query_parts)

    def _filter_by_audio_features(
        self,
        tracks: List[Dict],
        params: Dict[str, Any]
    ) -> List[Dict]:
        """
        Filter tracks based on audio features using ReccoBeats API,
        performing two steps: metadata lookup then audio feature lookup.
        """
        print(f"Starting audio features filtering with {len(tracks)} tracks.")
        if not tracks:
            print("No tracks to filter for audio features.")
            return []

        print(f"Filtering criteria: Tempo {params['tempo_range']}, Energy {params['energy_range']}, Valence {params['valence_range']}, Danceability {params['danceability_range']}")

        all_spotify_ids = [track.get('id') for track in tracks if track.get('id')]

        # Step 1: Get ReccoBeats metadata (which contains ReccoBeats IDs) for all Spotify IDs
        spotify_id_to_reccobeats_info_map = self._fetch_reccobeats_metadata_batch(all_spotify_ids)
        print(f"Step 1: Successfully mapped {len(spotify_id_to_reccobeats_info_map)} Spotify IDs to ReccoBeats info.")


        # Step 2: Fetch audio features for all available ReccoBeats IDs, prioritizing cache
        reccobeats_ids_to_fetch_audio_features = []
        for spotify_id, info in spotify_id_to_reccobeats_info_map.items():
            if info.get('reccobeats_id') not in _reccobeats_final_audio_features_cache and info.get('reccobeats_id'):
                reccobeats_ids_to_fetch_audio_features.append(info['reccobeats_id'])
        print(f"Step 2: Will attempt to fetch audio features for {len(reccobeats_ids_to_fetch_audio_features)} new ReccoBeats IDs.")

        for reccobeats_id in reccobeats_ids_to_fetch_audio_features:
            self._fetch_reccobeats_audio_features_single(reccobeats_id) # This call populates the cache


        filtered_tracks = []
        for track in tracks:
            spotify_id = track.get('id')
            if not spotify_id:
                continue

            # Get the ReccoBeats ID associated with this Spotify ID to retrieve features from cache
            reccobeats_info = spotify_id_to_reccobeats_info_map.get(spotify_id)
            reccobeats_id = reccobeats_info.get('reccobeats_id') if reccobeats_info else None

            # Retrieve features using the ReccoBeats ID from the cache
            features = _reccobeats_final_audio_features_cache.get(reccobeats_id)

            if features and self._matches_criteria(features, params):
                track['audio_features'] = features
                filtered_tracks.append(track)
            else:
                feature_status = "not found/retrieved" if not features else "did not match criteria"
                print(f"Track '{track.get('name', spotify_id)}' (Spotify ID: {spotify_id}) {feature_status}.")

        print(f"Finished audio features filtering. {len(filtered_tracks)} tracks passed.")
        return filtered_tracks

    def _matches_criteria(self, features: Dict, params: Dict[str, Any]) -> bool:
        """Check if track's audio features match the criteria."""
        tempo_min, tempo_max = params["tempo_range"]
        energy_min, energy_max = params["energy_range"]
        valence_min, valence_max = params["valence_range"]
        dance_min, dance_max = params["danceability_range"]
        
        return (
            tempo_min <= features.get('tempo', 0) <= tempo_max and
            energy_min <= features.get('energy', 0.0) <= energy_max and
            valence_min <= features.get('valence', 0.0) <= valence_max and
            dance_min <= features.get('danceability', 0.0) <= dance_max
        )

    def _select_tracks_for_duration(
        self,
        tracks: List[Dict],
        target_minutes: int
    ) -> List[Dict]:
        """Select tracks to approximately match target duration."""
        print(f"Starting duration selection with {len(tracks)} tracks.")
        if not tracks:
            print("No tracks to select for duration.")
            return []
        target_ms = target_minutes * 60 * 1000
        selected_tracks = []
        total_duration = 0
        shuffled_tracks = random.sample(tracks, len(tracks))
        for track in shuffled_tracks:
            track_duration = track.get('duration_ms')
            if track_duration is None:
                continue
            if total_duration + track_duration <= target_ms * 1.1:
                selected_tracks.append(track)
                total_duration += track_duration
                if total_duration >= target_ms * 0.9:
                    break
        print(f"Finished duration selection. {len(selected_tracks)} tracks selected.")
        return selected_tracks

    def _sort_tracks_by_energy_progression(self, tracks: List[Dict]) -> List[Dict]:
        """
        Sorts tracks to create a warm-up, peak, cool-down energy progression.
        Assumes tracks have 'audio_features' with an 'energy' key.
        """
        if not tracks:
            return []

        # Filter out tracks without energy features, although they should all have it by this stage
        tracks_with_energy = [t for t in tracks if t.get('audio_features') and 'energy' in t['audio_features']]
        if not tracks_with_energy:
            print("No tracks with energy features to sort for progression.")
            return tracks # Return original tracks if sorting is not possible

        # Sort all tracks by energy
        tracks_with_energy.sort(key=lambda t: t['audio_features']['energy'])

        total_tracks = len(tracks_with_energy)
        warm_up_size = max(1, int(total_tracks * 0.2)) # ~20% for warm-up
        cool_down_size = max(1, int(total_tracks * 0.2)) # ~20% for cool-down
        
        # Ensure cool_down_size doesn't overlap with warm_up_size too much if tracks are few
        if warm_up_size + cool_down_size > total_tracks:
            warm_up_size = int(total_tracks * 0.5)
            cool_down_size = total_tracks - warm_up_size
            if cool_down_size < 0: cool_down_size = 0 # Safety for very small lists


        warm_up_tracks = tracks_with_energy[:warm_up_size]
        # Middle tracks are for the peak
        peak_tracks = tracks_with_energy[warm_up_size : total_tracks - cool_down_size]
        cool_down_tracks = tracks_with_energy[total_tracks - cool_down_size:]

        # Sort warm-up tracks by ascending energy (already sorted)
        # Sort peak tracks by descending energy to get the highest first, then slightly lower within peak
        peak_tracks.sort(key=lambda t: t['audio_features']['energy'], reverse=True)
        # Sort cool-down tracks by descending energy to go from higher to lower
        cool_down_tracks.sort(key=lambda t: t['audio_features']['energy'], reverse=True)


        # For a smooth progression, a better approach for peak and cool-down:
        # Peak: Take a central portion of high-energy tracks.
        # Cool-down: Take the highest remaining energy tracks and sort them descending.

        # A simpler ramp-up, peak, ramp-down:
        # Warm-up: lowest energy tracks (already sorted ascending)
        # Peak: Remaining tracks sorted by descending energy (to have highest in middle)
        # Cool-down: last few tracks of the lowest energy (or highest energy in reverse)
        # Let's try this pattern: warm-up, then main body with some variation, then cool-down
        
        # A more common approach for warm-up/cool-down is a parabolic shape:
        # Sort all by energy.
        # Take first N for warm up (ascending).
        # Take last N for cool down (descending).
        # Remaining middle tracks can be shuffled or sorted based on preference.

        # Let's do a simple ascending for warm-up, then high for main, then descending for cool-down
        sorted_tracks = []

        # Warm-up (lowest energy)
        sorted_tracks.extend(warm_up_tracks)

        # Peak (highest energy tracks from the middle portion)
        # For simplicity, we can shuffle the peak tracks to avoid strict monotonic decrease
        # or sort by descending and then just pick some.
        # Let's try shuffling the peak to make it less predictable but generally high energy.
        random.shuffle(peak_tracks)
        sorted_tracks.extend(peak_tracks)

        # Cool-down (remaining tracks, sorted by descending energy for a smooth fade)
        sorted_tracks.extend(cool_down_tracks)

        print(f"Sorted tracks into warm-up ({len(warm_up_tracks)}), peak ({len(peak_tracks)}), cool-down ({len(cool_down_tracks)}) phases.")
        return sorted_tracks


    def create_playlist(
        self,
        name: str,
        description: str,
        track_uris: List[str],
        image_path: Optional[str] = None # New parameter for image path
    ) -> Optional[Dict[str, Any]]:
        """
        Creates a public playlist on the authenticated Spotify account, adds tracks,
        and optionally uploads a cover image.
        """
        if not self.sp or not self.user_id:
            print("Spotify client not authenticated or user ID not available. Cannot create playlist.")
            return None

        try:
            print(f"Attempting to create playlist '{name}' for user {self.user_id}...")
            playlist = self.sp.user_playlist_create(
                user=self.user_id,
                name=name,
                public=True,
                description=description
            )
            print(f"Playlist '{playlist['name']}' created with ID: {playlist['id']}")

            if track_uris:
                print(f"Adding {len(track_uris)} tracks to playlist {playlist['id']}...")
                for i in range(0, len(track_uris), 100):
                    self.sp.playlist_add_items(
                        playlist_id=playlist['id'],
                        items=track_uris[i:i+100]
                    )
                print(f"Successfully added {len(track_uris)} tracks.")

            image_url_result = None
            if image_path and os.path.exists(image_path):
                try:
                    with open(image_path, 'rb') as img_file:
                        image_data = img_file.read()
                    
                    image_data_base64 = base64.b64encode(image_data).decode('utf-8')
                    
                    print(f"Uploading cover image for playlist {playlist['id']} from {image_path}...")
                    self.sp.playlist_upload_cover_image(playlist['id'], image_data_base64)
                    print("Playlist cover image uploaded successfully!")
                    
                    updated_playlist = self.sp.playlist(playlist['id'], fields='images')
                    if updated_playlist and updated_playlist.get('images'):
                        image_url_result = updated_playlist['images'][0].get('url')
                    else:
                        print("Warning: Could not retrieve uploaded image URL from Spotify after upload.")

                except FileNotFoundError:
                    print(f"Warning: Image file not found at {image_path}. Skipping image upload.")
                except spotipy.exceptions.SpotifyException as e:
                    print(f"Spotify API Error uploading image: Status {e.http_status}, Code {e.code}, Message: {e.msg}")
                    print("HINT: Ensure the image is a JPEG and its size does not exceed 256KB and 'ugc-image-upload' scope is granted.")
                except Exception as e:
                    print(f"An unexpected error occurred during image upload: {e}")
            elif image_path:
                print(f"Warning: Image path '{image_path}' provided but file does not exist. Skipping image upload.")


            return {
                "playlist_id": playlist['id'],
                "playlist_url": playlist['external_urls']['spotify'],
                "name": playlist['name'],
                "description": playlist['description'],
                "track_count": len(track_uris),
                "image_url": image_url_result
            }
        except spotipy.exceptions.SpotifyException as e:
            print(f"Spotify API Error creating playlist: Status {e.http_status}, Code {e.code}, Message: {e.msg}")
            if e.http_status == 401:
                print("HINT: 401 Unauthorized. Your Spotify OAuth token might be expired or invalid. Try re-running the authentication script.")
            elif e.http_status == 403:
                print("HINT: 403 Forbidden. You might not have the required scopes (e.g., 'playlist-modify-public', 'ugc-image-upload'). Re-authenticate with correct scopes.")
            return None
        except Exception as e:
            print(f"Error creating playlist: {e}")
            return None

def create_activity_playlist(activity: str, vibe: str, duration: int = 30):
    """
    Main function to create a playlist based on user input.
    """
    spotify_service = SpotifyService()

    if not spotify_service.sp:
        return {"error": "Spotify service not authenticated. Cannot create playlist."}


    print("Attempting to create playlist...")

    # Pass total_fetch_limit to fetch more tracks initially
    # Increased total_fetch_limit to 200, can adjust further if needed
    tracks = spotify_service.search_tracks_by_criteria(
        activity=activity,
        vibe=vibe,
        duration_minutes=duration,
        total_fetch_limit=400 # Fetch up to 200 tracks initially
    )

    if not tracks:
        print("No tracks found after Spotify search and ReccoBeats filtering. Returning error.")
        return {"error": "No suitable tracks found"}

    returned_tracks = []
    for track in tracks:
        track_id = track.get('id')
        track_name = track.get('name')
        artist_name = "Unknown Artist"
        if track.get('artists') and isinstance(track['artists'], list) and len(track['artists']) > 0:
            artist_name = track['artists'][0].get('name', "Unknown Artist")

        spotify_url = track.get('external_urls', {}).get('spotify')
        preview_url = track.get('preview_url')
        duration_ms = track.get('duration_ms')

        album_data = track.get('album', {})
        album_name = album_data.get('name', "Unknown Album")
        album_image_url = album_data.get('images', [{}])[0].get('url') if album_data.get('images') and len(album_data['images']) > 0 else None

        if all([track_name, artist_name != "Unknown Artist", spotify_url, duration_ms is not None]):
            returned_tracks.append({
                "id": track_id,
                "name": track_name,
                "artist": artist_name,
                "album": {"name": album_name, "images": [{"url": album_image_url}] if album_image_url else []},
                "duration": duration_ms,
                "spotifyUrl": spotify_url,
                "previewUrl": preview_url
            })
        else:
            print(f"Skipping track due to missing essential data for final response: ID={track.get('id')}, Name={track.get('name')}")

    if not returned_tracks:
        print("No tracks remained after filtering for essential data for final response. Returning error.")
        return {"error": "No suitable tracks with complete data found"}

    try:
        total_duration_minutes_calculated = sum(t.get('duration', 0) for t in returned_tracks) / (1000 * 60)

        playlist_name = f"{vibe.capitalize()} {activity.capitalize()}"
        playlist_description = f"A {vibe} playlist for your {activity} session, approximately {int(total_duration_minutes_calculated)} minutes long."
        track_uris_for_spotify = [t['spotifyUrl'] for t in returned_tracks]

        # Corrected path for default playlist cover image: go up two levels from 'services' to 'backend'
        default_playlist_cover_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "default_playlist_cover.jpg")
        
        playlist_creation_result = spotify_service.create_playlist(
            name=playlist_name,
            description=playlist_description,
            track_uris=track_uris_for_spotify,
            image_path=default_playlist_cover_path
        )

        if not playlist_creation_result:
            print("Failed to create Spotify playlist. Check logs for Spotify API errors.")
            return {"error": "Failed to create playlist on Spotify."}

        return {
            "tracks": returned_tracks,
            "total_duration_minutes": total_duration_minutes_calculated,
            "criteria": {
                "activity": activity,
                "vibe": vibe,
                "target_duration": duration
            },
            "playlist_id": playlist_creation_result['playlist_id'],
            "playlist_url": playlist_creation_result['playlist_url'],
            "playlist_name": playlist_creation_result['name'],
            "playlist_description": playlist_creation_result['description'],
            "playlist_image_url": playlist_creation_result.get('image_url', "https://via.placeholder.com/300x300.png?text=Playlist+Image")
        }
    except Exception as e:
        print(f"CRITICAL ERROR during final playlist response construction/creation: {e}")
        raise
