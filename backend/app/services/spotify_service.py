# backend/app/services/spotify_service.py

import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import List, Dict, Any, Optional
import random
import http.client
import json
import urllib.parse

_reccobeats_final_audio_features_cache = {}

class SpotifyService:
    def __init__(self):
        """Initialize Spotify client with client credentials flow."""
        client_id = os.getenv("SPOTIFY_CLIENT_ID")
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        client_credentials_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

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
                        print(f"ReccoBeats API Error: Unexpected response format for metadata batch {batch_spotify_ids}. Response: {data}")
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
           
            print(data)

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
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Search for tracks based on activity and vibe.
        """
        search_params = self._convert_to_search_params(activity, vibe)
        query = self._build_search_query(activity, search_params)

        print(f"Spotify search query: '{query}', limit: {limit}")
        results = self.sp.search(
            q=query,
            type='track',
            limit=limit,
            market='US'
        )
        tracks = results['tracks']['items']
        print(f"Spotify search returned {len(tracks)} tracks.")

        filtered_tracks = self._filter_by_audio_features(tracks, search_params)
        print(f"After audio features filtering, {len(filtered_tracks)} tracks remain.")

        selected_tracks = self._select_tracks_for_duration(
            filtered_tracks,
            duration_minutes
        )
        print(f"After duration selection, {len(selected_tracks)} tracks remain.")
        return selected_tracks

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
            # Add specific mapping for 'dance pop' to ensure correct criteria are used
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
            if spotify_id not in _reccobeats_final_audio_features_cache and info.get('reccobeats_id'):
                reccobeats_ids_to_fetch_audio_features.append(info['reccobeats_id'])
        print(f"Step 2: Will attempt to fetch audio features for {len(reccobeats_ids_to_fetch_audio_features)} new ReccoBeats IDs.")

        for reccobeats_id in reccobeats_ids_to_fetch_audio_features:
            self._fetch_reccobeats_audio_features_single(reccobeats_id) # This call populates the cache

        for i, entry in enumerate(_reccobeats_final_audio_features_cache):
            print(f"[{i}] {entry}")

        filtered_tracks = []
        for track in tracks:
            spotify_id = track.get('id')
            print (f"Spotify ID = {spotify_id}")
            if not spotify_id:
                print("no spotify ids")
                continue
            reccobeats_id = spotify_id_to_reccobeats_info_map.get(spotify_id)['reccobeats_id']
            print(f"Reccobeats ID = {reccobeats_id}")

            try:
                if not _reccobeats_final_audio_features_cache.__contains__(reccobeats_id):
                    print("Not found in cache")
                    continue
                else:
                    print("Found in cache")

                features = _reccobeats_final_audio_features_cache.get(reccobeats_id)
                print(f"{spotify_id} - " + features)
            except Exception as e:
                print(f"Error getting audio features from cache: {e}")


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

    def create_playlist(
        self,
        user_id: str,
        name: str,
        description: str,
        track_uris: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Create a public playlist and add tracks.
        """
        try:
            playlist = self.sp.user_playlist_create(
                user=user_id,
                name=name,
                public=True,
                description=description
            )
            if track_uris:
                self.sp.playlist_add_items(
                    playlist_id=playlist['id'],
                    items=track_uris
                )
            return {
                "playlist_id": playlist['id'],
                "playlist_url": playlist['external_urls']['spotify'],
                "name": playlist['name'],
                "track_count": len(track_uris)
            }
        except Exception as e:
            print(f"Error creating playlist: {e}")
            return None

def create_activity_playlist(activity: str, vibe: str, duration: int = 30):
    """
    Main function to create a playlist based on user input.
    """
    spotify_service = SpotifyService()

    print("Attempting to create playlist...")

    tracks = spotify_service.search_tracks_by_criteria(
        activity=activity,
        vibe=vibe,
        duration_minutes=duration
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

        if all([track_name, artist_name != "Unknown Artist", spotify_url, duration_ms is not None]):
            returned_tracks.append({
                "name": track_name,
                "artist": artist_name,
                "spotify_url": spotify_url,
                "preview_url": preview_url,
                "duration_ms": duration_ms
            })
        else:
            print(f"Skipping track due to missing essential data for final response: ID={track.get('id')}, Name={track.get('name')}")

    if not returned_tracks:
        print("No tracks remained after filtering for essential data for final response. Returning error.")
        return {"error": "No suitable tracks with complete data found"}

    try:
        total_duration_minutes_calculated = sum(t.get('duration_ms', 0) for t in returned_tracks) / (1000 * 60)

        return {
            "tracks": returned_tracks,
            "total_duration_minutes": total_duration_minutes_calculated,
            "criteria": {
                "activity": activity,
                "vibe": vibe,
                "target_duration": duration
            }
        }
    except Exception as e:
        print(f"CRITICAL ERROR during final playlist response construction: {e}")
        raise
