# backend/app/services/spotify_service.py
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import List, Dict, Any, Optional
import random

class SpotifyService:
    def __init__(self):
        """Initialize Spotify client with client credentials flow."""
        print("Initialising spotify service")
        client_credentials_manager = SpotifyClientCredentials(
            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
        )
        self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        
    def search_tracks_by_criteria(
        self, 
        activity: str, 
        vibe: str, 
        duration_minutes: int = 30,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Search for tracks based on activity and vibe.
        
        Args:
            activity: User's activity (e.g., "yoga", "studying", "cleaning")
            vibe: User's desired vibe ("chill", "upbeat")
            duration_minutes: Target playlist duration
            limit: Number of tracks to fetch for selection
            
        Returns:
            List of track dictionaries with metadata
        """
        # Convert user input to Spotify search parameters
        search_params = self._convert_to_search_params(activity, vibe)
        
        # Build search query
        query = self._build_search_query(activity, search_params)
        
        # Search for tracks
        results = self.sp.search(
            q=query,
            type='track',
            limit=limit,
            market='US'
        )
        
        # Filter tracks by audio features
        tracks = results['tracks']['items']
        filtered_tracks = self._filter_by_audio_features(tracks, search_params)
        
        # Select tracks to meet target duration
        selected_tracks = self._select_tracks_for_duration(
            filtered_tracks, 
            duration_minutes
        )
        
        return selected_tracks
    
    def _convert_to_search_params(self, activity: str, vibe: str) -> Dict[str, Any]:
        """Convert user input to Spotify audio feature parameters."""
        
        # Vibe mappings
        vibe_mappings = {
            "chill": {
                "tempo_range": (60, 100),
                "energy_range": (0.1, 0.6),
                "valence_range": (0.2, 0.8),
                "danceability_range": (0.2, 0.7)
            },
            "upbeat": {
                "tempo_range": (110, 180),
                "energy_range": (0.6, 1.0),
                "valence_range": (0.5, 1.0),
                "danceability_range": (0.5, 1.0)
            }
        }
        
        # Activity-specific keywords and adjustments
        activity_mappings = {
            "yoga": {
                "keywords": ["ambient", "meditation", "peaceful", "zen"],
                "tempo_adjustment": -10,  # Slightly slower
                "energy_adjustment": -0.2
            },
            "studying": {
                "keywords": ["focus", "instrumental", "ambient", "lo-fi"],
                "tempo_adjustment": 0,
                "energy_adjustment": -0.3
            },
            "cleaning": {
                "keywords": ["energetic", "pop", "dance"],
                "tempo_adjustment": +15,
                "energy_adjustment": +0.1
            },
            "workout": {
                "keywords": ["pump up", "energetic", "motivation"],
                "tempo_adjustment": +20,
                "energy_adjustment": +0.2
            },
            "cooking": {
                "keywords": ["uplifting", "feel good", "positive"],
                "tempo_adjustment": +5,
                "energy_adjustment": 0
            }
        }
        
        # Get base parameters from vibe
        base_params = vibe_mappings.get(vibe.lower(), vibe_mappings["chill"])
        
        # Get activity-specific adjustments
        activity_config = activity_mappings.get(
            activity.lower(), 
            {"keywords": [], "tempo_adjustment": 0, "energy_adjustment": 0}
        )
        
        # Apply adjustments
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
        
        # Add activity as base search term
        query_parts.append(activity)
        
        # Add activity-specific keywords
        if params["keywords"]:
            # Pick 1-2 random keywords to avoid overly restrictive searches
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
        """Filter tracks based on audio features."""
        if not tracks:
            return []
        
        # Get track IDs
        track_ids = [track['id'] for track in tracks if track['id']]
        
        # Get audio features for all tracks
        audio_features = self.sp.audio_features(track_ids)
        
        filtered_tracks = []
        for track, features in zip(tracks, audio_features):
            if features and self._matches_criteria(features, params):
                track['audio_features'] = features
                filtered_tracks.append(track)
        
        return filtered_tracks
    
    def _matches_criteria(self, features: Dict, params: Dict[str, Any]) -> bool:
        """Check if track's audio features match the criteria."""
        tempo_min, tempo_max = params["tempo_range"]
        energy_min, energy_max = params["energy_range"]
        valence_min, valence_max = params["valence_range"]
        dance_min, dance_max = params["danceability_range"]
        
        return (
            tempo_min <= features['tempo'] <= tempo_max and
            energy_min <= features['energy'] <= energy_max and
            valence_min <= features['valence'] <= valence_max and
            dance_min <= features['danceability'] <= dance_max
        )
    
    def _select_tracks_for_duration(
        self, 
        tracks: List[Dict], 
        target_minutes: int
    ) -> List[Dict]:
        """Select tracks to approximately match target duration."""
        if not tracks:
            return []
        
        target_ms = target_minutes * 60 * 1000
        selected_tracks = []
        total_duration = 0
        
        # Shuffle tracks for variety
        shuffled_tracks = random.sample(tracks, len(tracks))
        
        for track in shuffled_tracks:
            track_duration = track['duration_ms']
            if total_duration + track_duration <= target_ms * 1.1:  # 10% buffer
                selected_tracks.append(track)
                total_duration += track_duration
                
                if total_duration >= target_ms * 0.9:  # At least 90% of target
                    break
        
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
        
        Note: This requires user authentication, not client credentials.
        For your use case, you'll need to authenticate with your own account
        and create playlists on your account.
        """
        try:
            # Create playlist
            playlist = self.sp.user_playlist_create(
                user=user_id,
                name=name,
                public=True,
                description=description
            )
            
            # Add tracks to playlist
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

# Usage example
def create_activity_playlist(activity: str, vibe: str, duration: int = 30):
    """
    Main function to create a playlist based on user input.
    
    Args:
        activity: User's activity
        vibe: User's vibe preference
        duration: Playlist duration in minutes
        
    Returns:
        Dict with playlist info and track list
    """
    spotify_service = SpotifyService()
    
    # Search for tracks
    tracks = spotify_service.search_tracks_by_criteria(
        activity=activity,
        vibe=vibe,
        duration_minutes=duration
    )
    
    if not tracks:
        return {"error": "No suitable tracks found"}
    
    # For now, return track info without creating actual playlist
    # (since that requires user auth)
    return {
        "tracks": [
            {
                "name": track['name'],
                "artist": track['artists'][0]['name'],
                "spotify_url": track['external_urls']['spotify'],
                "preview_url": track['preview_url'],
                "duration_ms": track['duration_ms']
            }
            for track in tracks
        ],
        "total_duration_minutes": sum(t['duration_ms'] for t in tracks) / (1000 * 60),
        "criteria": {
            "activity": activity,
            "vibe": vibe,
            "target_duration": duration
        }
    }
