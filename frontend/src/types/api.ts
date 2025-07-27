
export interface PlaylistRequest {
  activity: string
  duration: number
  vibe: string
}

export interface PlaylistResponse {
  id: string
  name: string
  description: string
  spotifyUrl: string
  imageUrl: string
  tracks: Track[]
  duration: number
  createdAt: string
  // NEW: Include activity and vibe in API response
  activity: string
  vibe: string
}

export interface SpotifyAlbum {
  album_type: string
  artists: SpotifyArtist[]
  available_markets: string[]
  external_urls: {
    spotify: string
  }
  href: string
  id: string
  images: SpotifyImage[]
  is_playable?: boolean
  name: string
  release_date: string
  release_date_precision: string
  total_tracks: number
  type: string
  uri: string
}

export interface SpotifyArtist {
  external_urls: {
    spotify: string
  }
  href: string
  id: string
  name: string
  type: string
  uri: string
}

export interface SpotifyImage {
  height: number
  url: string
  width: number
}

export interface Track {
  id: string
  name: string
  artist: string
  album: SpotifyAlbum
  duration: number
  spotifyUrl: string
  previewUrl?: string
}

export interface ApiError {
  message: string
  code?: string
  details?: unknown
}