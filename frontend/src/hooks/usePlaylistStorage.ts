import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import type { PlaylistResponse } from '@/types/api'

const STORAGE_KEY = 'user_playlists'
const QUERY_KEY = ['playlists'] as const

// NOW: StoredPlaylist is just an alias for PlaylistResponse
export type StoredPlaylist = PlaylistResponse

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
    mutationFn: async (playlistResponse: PlaylistResponse) => {
      // SIMPLIFIED: Just store the PlaylistResponse directly
      const currentPlaylists = loadPlaylistsFromStorage()
      const updatedPlaylists = [playlistResponse, ...currentPlaylists]
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
  const addPlaylist = (playlistResponse: PlaylistResponse) => {
    return addPlaylistMutation.mutateAsync(playlistResponse)
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
    isAdding: addPlaylistMutation.isPending,
    isRemoving: removePlaylistMutation.isPending,
  }
}