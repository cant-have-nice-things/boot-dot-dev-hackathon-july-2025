import { useMutation } from '@tanstack/react-query'
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
