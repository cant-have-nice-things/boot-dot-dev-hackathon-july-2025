// src/types/api.ts

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
  tracks: Track[]
  duration: number
  createdAt: string
}

export interface Track {
  id: string
  name: string
  artist: string
  album: string
  duration: number
  spotifyUrl: string
  previewUrl?: string
}

export interface ApiError {
  message: string
  code?: string
  details?: unknown
}
