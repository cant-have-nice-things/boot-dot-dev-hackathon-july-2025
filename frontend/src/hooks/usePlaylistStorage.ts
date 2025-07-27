// frontend/src/hooks/usePlaylistStorage.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import type { PlaylistResponse } from '@/types/api'

const STORAGE_KEY = 'user_playlists'
const QUERY_KEY = ['playlists'] as const

export interface StoredPlaylist {
  id: string
  name: string
  description: string
  imageUrl: string
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
        imageUrl: playlistResponse.imageUrl,
        activity: originalRequest.activity,
        vibe: originalRequest.vibe,
        duration: playlistResponse.duration,
        trackCount: playlistResponse.tracks.length,
        createdAt: playlistResponse.createdAt,
        spotifyUrl: playlistResponse.spotifyUrl,
      }

      const currentPlaylists = loadPlaylistsFromStorage()
      const updatedPlaylists = [storedPlaylist, ...currentPlaylists]
      return savePlaylistsToStorage(updatedPlaylists)
    },
    onSuccess: (updatedPlaylists) => {
      queryClient.setQueryData(QUERY_KEY, updatedPlaylists)
    },
  })

  // Mutation for removing a playlist
  const removePlaylistMutation = useMutation({
    mutationFn: async (playlistId: string) => {
      const currentPlaylists = loadPlaylistsFromStorage()
      const filteredPlaylists = currentPlaylists.filter(p => p.id !== playlistId)
      return savePlaylistsToStorage(filteredPlaylists)
    },
    onSuccess: (updatedPlaylists) => {
      queryClient.setQueryData(QUERY_KEY, updatedPlaylists)
    },
  })

  // Convenience methods
  const addPlaylist = (
      playlistResponse: PlaylistResponse,
      originalRequest: { activity: string; vibe: string }
  ) => {
    return addPlaylistMutation.mutateAsync({ playlistResponse, originalRequest })
  }

  const removePlaylist = (playlistId: string) => {
    return removePlaylistMutation.mutateAsync(playlistId)
  }

  const getPlaylistById = (id: string): StoredPlaylist | undefined => {
    return playlists.find(p => p.id === id)
  }

  const hasPlaylists = playlists.length > 0

  const getRecentPlaylists = (count: number): StoredPlaylist[] => {
    return playlists
        .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
        .slice(0, count)
  }

  // Add a method to save a shared playlist
  const addSharedPlaylist = async (playlistResponse: PlaylistResponse, activity?: string, vibe?: string) => {
    const originalRequest = {
      activity: activity || 'Shared Activity',
      vibe: vibe || 'mixed'
    }
    return addPlaylist(playlistResponse, originalRequest)
  }

  return {
    playlists,
    isLoading,
    error,
    isError,
    addPlaylist,
    removePlaylist,
    getPlaylistById,
    hasPlaylists,
    getRecentPlaylists,
    addSharedPlaylist, // New method for shared playlists
    isAdding: addPlaylistMutation.isPending,
    isRemoving: removePlaylistMutation.isPending,
  }
}