import type { PlaylistRequest, PlaylistResponse } from '@/types/api'

const API_BASE_URL = import.meta.env?.VITE_API_URL || 'http://localhost:8000'

class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`

    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.message || `HTTP Error: ${response.status} ${response.statusText}`)
    }

    return response.json()
  }

  async generatePlaylist(data: PlaylistRequest): Promise<PlaylistResponse> {
    // For now, return a mock response until backend is ready
    // TODO: Replace with actual API call when backend endpoint is ready
    await new Promise(resolve => setTimeout(resolve, 2000)) // Simulate network delay

    return {
      id: `playlist_${Date.now()}`,
      name: `${data.activity} Vibes`,
      description: `A ${data.vibe} playlist for ${data.activity} (${data.duration} minutes)`,
      spotifyUrl: 'https://open.spotify.com/playlist/mock',
      duration: data.duration,
      createdAt: new Date().toISOString(),
      tracks: [
        {
          id: 'track1',
          name: 'Sample Song 1',
          artist: 'Sample Artist',
          album: 'Sample Album',
          duration: 210,
          spotifyUrl: 'https://open.spotify.com/track/mock1',
          previewUrl: 'https://example.com/preview1.mp3',
        },
        {
          id: 'track2',
          name: 'Sample Song 2',
          artist: 'Another Artist',
          album: 'Another Album',
          duration: 195,
          spotifyUrl: 'https://open.spotify.com/track/mock2',
        },
      ],
    }

    // When backend is ready, replace above mock with:
    // return this.request<PlaylistResponse>('/api/generate-playlist', {
    //   method: 'POST',
    //   body: JSON.stringify(data),
    // })
  }
}

export const apiClient = new ApiClient()
