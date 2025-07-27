import type { PlaylistRequest, PlaylistResponse } from '@/types/api'

const API_BASE_URL = import.meta.env?.VITE_API_URL || 'http://localhost:8000'

class ApiClient {
  private baseUrl: string
  private apiRouteV1: string = '/api/v1'

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
    return this.request<PlaylistResponse>(`${this.apiRouteV1}/generate-playlist`, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async getPlaylistById(playlistId: string): Promise<PlaylistResponse> {
    return this.request<PlaylistResponse>(`${this.apiRouteV1}/playlist/${playlistId}`)
  }
}

export const apiClient = new ApiClient()
