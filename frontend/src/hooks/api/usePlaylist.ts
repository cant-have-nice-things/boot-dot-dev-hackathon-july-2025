import { useMutation, useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import type { PlaylistRequest, PlaylistResponse } from '@/types/api'

export const useGeneratePlaylist = () => {
  return useMutation<PlaylistResponse, Error, PlaylistRequest>({
    mutationFn: (data: PlaylistRequest) => apiClient.generatePlaylist(data),
    onSuccess: data => {
      console.log('Playlist generated successfully:', data)
    },
    onError: error => {
      console.error('Failed to generate playlist:', error)
    },
  })
}

export const useFetchPlaylist = (playlistId: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: ['playlist', playlistId],
    queryFn: () => apiClient.getPlaylistById(playlistId),
    enabled: enabled && !!playlistId,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 1, // Only retry once for shared playlists
  })
}