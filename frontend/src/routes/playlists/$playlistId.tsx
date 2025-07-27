import { createFileRoute } from '@tanstack/react-router'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ArrowLeft, Music, ExternalLink, Share2, Download } from 'lucide-react'
import { Link } from '@tanstack/react-router'
import { ShareDialog } from '@/components/ShareDialog'
import { usePlaylistStorage } from '@/hooks/usePlaylistStorage'
import { useGetPlaylist } from '@/hooks/api/usePlaylist'
import { useEffect } from 'react'

export const Route = createFileRoute('/playlists/$playlistId')({
  component: PlaylistDetail,
})

function PlaylistDetail() {
  const { playlistId } = Route.useParams()
  const { getPlaylistById, addPlaylist, isLoading: isLoadingStorage } = usePlaylistStorage()

  // Check if playlist exists in local storage
  const localPlaylist = getPlaylistById(playlistId)

  // Only fetch from API if:
  // 1. localStorage has finished loading, AND
  // 2. No playlist found in localStorage
  const shouldFetchFromAPI = !isLoadingStorage && !localPlaylist

  console.log('Playlist logic:', {
    playlistId,
    hasLocalPlaylist: !!localPlaylist,
    isLoadingStorage,
    shouldFetchFromAPI,
    localTrackCount: localPlaylist?.tracks?.length
  })

  // If not in local storage, try to fetch from API (shared playlist scenario)
  const {
    data: fetchedPlaylist,
    isLoading: isLoadingAPI,
    error
  } = useGetPlaylist(playlistId, shouldFetchFromAPI)

  // SIMPLIFIED: Both local and fetched playlists are now the same type
  const playlist = localPlaylist || fetchedPlaylist
  const isFromLocal = !!localPlaylist
  const isFromAPI = !!fetchedPlaylist && !localPlaylist

  // Auto-save fetched playlist to local storage (shared playlist scenario)
  useEffect(() => {
    if (fetchedPlaylist && !localPlaylist) {
      addPlaylist(fetchedPlaylist) // SIMPLIFIED: No need for mapping or extra parameters
          .then(() => {
            console.log('Shared playlist automatically saved to local storage')
          })
          .catch((err) => {
            console.error('Failed to auto-save playlist:', err)
          })
    }
  }, [fetchedPlaylist, localPlaylist, addPlaylist])

  if (isLoadingStorage || (shouldFetchFromAPI && isLoadingAPI)) {
    return (
        <div className="container mx-auto px-4 py-16">
          <div className="max-w-2xl mx-auto text-center space-y-6">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
            <h1 className="text-2xl font-bold">Loading Playlist...</h1>
            <p className="text-muted-foreground">
              {isLoadingStorage ? 'Checking your saved playlists...' : 'Fetching playlist details from the server.'}
            </p>
          </div>
        </div>
    )
  }

  if (error || !playlist) {
    return (
        <div className="container mx-auto px-4 py-16">
          <div className="max-w-2xl mx-auto text-center space-y-6">
            <h1 className="text-2xl font-bold">Playlist Not Found</h1>
            <p className="text-muted-foreground">
              {error ? 'This playlist could not be loaded from the server.' : 'This playlist doesn\'t exist.'}
            </p>
            <Link to="/">
              <Button variant="outline">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Generator
              </Button>
            </Link>
          </div>
        </div>
    )
  }

  const getVibeColor = (vibe: string) => {
    const colors: Record<string, string> = {
      chill: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      upbeat: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
      focus: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      energetic: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
      mellow: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
      ambient: 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200',
    }
    return colors[vibe.toLowerCase()] || colors.chill
  }

  // SIMPLIFIED: No need for type checking or fallbacks - activity and vibe are always present
  const tracks = playlist.tracks || []
  const hasFullTrackData = tracks.length > 0

  return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto space-y-8">
          {/* Header */}
          <div className="flex items-center gap-4">
            <Link to="/">
              <Button variant="outline" size="sm">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Create New Playlist
              </Button>
            </Link>
          </div>

          {/* Auto-saved notification - only show if this was a shared playlist */}
          {isFromAPI && (
              <Card className="border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-950">
                <CardContent className="pt-6">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-green-100 dark:bg-green-900 flex items-center justify-center">
                      <Download className="w-4 h-4 text-green-600 dark:text-green-400" />
                    </div>
                    <div>
                      <h3 className="font-medium text-green-900 dark:text-green-100">Shared Playlist Saved</h3>
                      <p className="text-sm text-green-700 dark:text-green-300">
                        This playlist has been automatically added to your collection.
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
          )}

          {/* Debug info in development */}
          {process.env.NODE_ENV === 'development' && (
              <Card className="border-yellow-200 bg-yellow-50 dark:border-yellow-800 dark:bg-yellow-950">
                <CardContent className="pt-6">
                  <div className="text-sm">
                    <strong>Debug:</strong> Source: {isFromLocal ? 'Local Storage' : 'API'} |
                    Tracks: {tracks.length} |
                    Has Album Art: {tracks.some(t => t.album?.images?.length > 0) ? 'Yes' : 'No'}
                  </div>
                </CardContent>
              </Card>
          )}

          {/* Playlist Overview */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-3">
                <Music className="w-6 h-6" />
                {playlist.name}
              </CardTitle>
              <CardDescription>{playlist.description}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Tags */}
              <div className="flex flex-wrap gap-2">
                <Badge variant="secondary" className="text-sm">
                  <Music className="w-3 h-3 mr-1" />
                  {playlist.activity}
                </Badge>
                <Badge className={`text-sm ${getVibeColor(playlist.vibe)}`}>
                  {playlist.vibe}
                </Badge>
                <Badge variant="outline" className="text-sm">
                  {tracks.length} tracks • {playlist.duration} min
                </Badge>
              </div>

              {/* Actions */}
              <div className="flex gap-3">
                <Button onClick={() => window.open(playlist.spotifyUrl, '_blank')} className="flex-1">
                  <ExternalLink className="w-4 h-4 mr-2" />
                  Open in Spotify
                </Button>
                <ShareDialog playlistName={playlist.name}>
                  <Button variant="outline">
                    <Share2 className="w-4 h-4 mr-2" />
                    Share Playlist
                  </Button>
                </ShareDialog>
              </div>
            </CardContent>
          </Card>

          {/* Track List */}
          <Card>
            <CardHeader>
              <CardTitle>Track List</CardTitle>
              <CardDescription>
                {hasFullTrackData ?
                    `${tracks.length} tracks with full album artwork and details` :
                    'Track information is not available for this playlist'
                }
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {hasFullTrackData ? (
                    tracks.map((track) => {
                      // Get album artwork (smallest available image for list view)
                      const albumImage = track.album?.images?.find(img => img.height <= 300) ||
                          track.album?.images?.[track.album.images.length - 1];

                      return (
                          <div key={track.id} className="flex items-center gap-4 p-3 rounded-lg border">
                            {/* Album artwork or fallback */}
                            <div className="w-12 h-12 bg-muted rounded-md flex items-center justify-center overflow-hidden relative">
                              {albumImage ? (
                                  <>
                                    <img
                                        src={albumImage.url}
                                        alt={`${track.album?.name || 'Album'} cover`}
                                        className="w-full h-full object-cover"
                                        onError={(e) => {
                                          // Fallback to music icon if image fails to load
                                          const target = e.currentTarget as HTMLImageElement;
                                          target.style.display = 'none';
                                          const fallback = target.nextElementSibling as HTMLElement;
                                          if (fallback) fallback.style.display = 'flex';
                                        }}
                                    />
                                    <Music className="w-5 h-5 text-muted-foreground absolute inset-0 m-auto hidden" />
                                  </>
                              ) : (
                                  <Music className="w-5 h-5 text-muted-foreground" />
                              )}
                            </div>

                            <div className="flex-1">
                              <div className="font-medium">{track.name}</div>
                              <div className="text-sm text-muted-foreground">
                                {track.artist} • {track.album?.name || 'Unknown Album'}
                              </div>
                            </div>

                            <div className="text-sm text-muted-foreground">
                              {Math.floor(track.duration / (1000 * 60))}:
                              {String(Math.floor(track.duration / 1000) % 60).padStart(2, '0')}
                            </div>

                            {track.spotifyUrl && (
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => window.open(track.spotifyUrl, '_blank')}
                                >
                                  <ExternalLink className="w-4 h-4" />
                                </Button>
                            )}
                          </div>
                      );
                    })
                ) : (
                    <div className="text-center py-8 text-muted-foreground">
                      <Music className="w-12 h-12 mx-auto mb-4 opacity-50" />
                      <p>Track details are not available for this playlist.</p>
                    </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
  )
}