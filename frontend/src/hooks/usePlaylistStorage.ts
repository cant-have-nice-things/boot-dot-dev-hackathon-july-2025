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
      // FIX: Use the current cache data instead of reading from localStorage again
      // This ensures we're working with the most up-to-date state
      const currentPlaylists = queryClient.getQueryData(QUERY_KEY) as StoredPlaylist[] || []
      const updatedPlaylists = [playlistResponse, ...currentPlaylists]
      return savePlaylistsToStorage(updatedPlaylists)
    },
    onSuccess: (updatedPlaylists) => {
      queryClient.setQueryData(QUERY_KEY, updatedPlaylists)
    },
    onError: (error) => {
      console.error('Failed to add playlist:', error)
      // Optionally refresh from storage on error
      queryClient.invalidateQueries({ queryKey: QUERY_KEY })
    }
  })

  // Mutation for removing a playlist
  const removePlaylistMutation = useMutation({
    mutationFn: async (playlistId: string) => {
      // FIX: Use the current cache data instead of reading from localStorage again
      const currentPlaylists = queryClient.getQueryData(QUERY_KEY) as StoredPlaylist[] || []
      const filteredPlaylists = currentPlaylists.filter(p => p.id !== playlistId)
      return savePlaylistsToStorage(filteredPlaylists)
    },
    onSuccess: (updatedPlaylists) => {
      queryClient.setQueryData(QUERY_KEY, updatedPlaylists)
    },
    onError: (error) => {
      console.error('Failed to remove playlist:', error)
      // Optionally refresh from storage on error
      queryClient.invalidateQueries({ queryKey: QUERY_KEY })
    }
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