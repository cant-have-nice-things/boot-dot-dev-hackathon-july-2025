// src/hooks/usePlaylistStorage.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import type { PlaylistResponse } from '@/types/api'

const STORAGE_KEY = 'user_playlists'
const QUERY_KEY = ['playlists'] as const

export interface StoredPlaylist {
  id: string
  name: string
  description: string
  activity: string
  vibe: string
  duration: number
  trackCount: number
  createdAt: string
  spotifyUrl: string
}

// Helper functions for localStorage operations
const loadPlaylistsFromStorage = (): StoredPlaylist[] => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      const parsed = JSON.parse(stored)
      return Array.isArray(parsed) ? parsed : []
    }
    return []
  } catch (error) {
    console.error('Failed to load playlists from storage:', error)
    return []
  }
}

const savePlaylistsToStorage = async (playlists: StoredPlaylist[]): Promise<StoredPlaylist[]> => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(playlists))
    return playlists
  } catch (error) {
    console.error('Failed to save playlists to storage:', error)
    throw error
  }
}

export const usePlaylistStorage = () => {
  const queryClient = useQueryClient()

  // Query for reading playlists from localStorage
  const {
    data: playlists = [],
    isLoading,
    error,
    isError,
  } = useQuery({
    queryKey: QUERY_KEY,
    queryFn: loadPlaylistsFromStorage,
    staleTime: Infinity, // Never stale since it's local data
    gcTime: Infinity, // Keep in cache forever
  })

  // Mutation for adding a playlist
  const addPlaylistMutation = useMutation({
    mutationFn: async ({
      playlistResponse,
      originalRequest,
    }: {
      playlistResponse: PlaylistResponse
      originalRequest: { activity: string; vibe: string }
    }) => {
      const storedPlaylist: StoredPlaylist = {
        id: playlistResponse.id,
        name: playlistResponse.name,
        description: playlistResponse.description,
        activity: originalRequest.activity,
        vibe: originalRequest.vibe,
        duration: playlistResponse.duration,
        trackCount: playlistResponse.tracks.length,
        createdAt: playlistResponse.createdAt,
        spotifyUrl: playlistResponse.spotifyUrl,
      }

      const currentPlaylists = queryClient.getQueryData<StoredPlaylist[]>(QUERY_KEY) || []
      const updatedPlaylists = [storedPlaylist, ...currentPlaylists]

      return await savePlaylistsToStorage(updatedPlaylists)
    },
    onSuccess: updatedPlaylists => {
      queryClient.setQueryData(QUERY_KEY, updatedPlaylists)
    },
    onError: error => {
      console.error('Failed to add playlist:', error)
    },
  })

  // Mutation for removing a playlist
  const removePlaylistMutation = useMutation({
    mutationFn: async (playlistId: string) => {
      const currentPlaylists = queryClient.getQueryData<StoredPlaylist[]>(QUERY_KEY) || []
      const updatedPlaylists = currentPlaylists.filter(playlist => playlist.id !== playlistId)

      return await savePlaylistsToStorage(updatedPlaylists)
    },
    onSuccess: updatedPlaylists => {
      queryClient.setQueryData(QUERY_KEY, updatedPlaylists)
    },
    onError: error => {
      console.error('Failed to remove playlist:', error)
    },
  })

  // Mutation for clearing all playlists
  const clearAllPlaylistsMutation = useMutation({
    mutationFn: async () => await savePlaylistsToStorage([]),
    onSuccess: updatedPlaylists => {
      queryClient.setQueryData(QUERY_KEY, updatedPlaylists)
    },
    onError: error => {
      console.error('Failed to clear playlists:', error)
    },
  })

  // Helper functions
  const addPlaylist = (
    playlistResponse: PlaylistResponse,
    originalRequest: { activity: string; vibe: string }
  ) => {
    addPlaylistMutation.mutate({ playlistResponse, originalRequest })
  }

  const removePlaylist = (id: string) => {
    removePlaylistMutation.mutate(id)
  }

  const clearAllPlaylists = () => {
    clearAllPlaylistsMutation.mutate()
  }

  const getPlaylistById = (id: string) => {
    return playlists.find(playlist => playlist.id === id)
  }

  const getRecentPlaylists = (count: number = 5) => {
    return playlists.slice(0, count)
  }

  return {
    // Data
    playlists,
    isLoading,
    isError,
    error,

    // Actions
    addPlaylist,
    removePlaylist,
    clearAllPlaylists,

    // Helpers
    getPlaylistById,
    getRecentPlaylists,

    // Computed values
    hasPlaylists: playlists.length > 0,
    playlistCount: playlists.length,

    // Mutation states for UI feedback
    isAddingPlaylist: addPlaylistMutation.isPending,
    isRemovingPlaylist: removePlaylistMutation.isPending,
    isClearingPlaylists: clearAllPlaylistsMutation.isPending,
  }
}
