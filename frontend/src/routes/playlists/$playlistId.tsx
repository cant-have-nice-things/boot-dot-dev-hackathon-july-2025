import { createFileRoute } from '@tanstack/react-router'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Music, ExternalLink, ArrowLeft, Share2, Download } from 'lucide-react'
import { Link } from '@tanstack/react-router'
import { usePlaylistStorage } from '@/hooks/usePlaylistStorage'
import { useFetchPlaylist } from '@/hooks/api/usePlaylist'
import { useToast } from '@/hooks/useToast'
import { ShareDialog } from '@/components/ShareDialog'
import { useEffect } from 'react'

export const Route = createFileRoute('/playlists/$playlistId')({
  component: PlaylistDetails,
})

function PlaylistDetails() {
  const { playlistId } = Route.useParams()
  const { getPlaylistById, addSharedPlaylist, isLoading: isLoadingStorage } = usePlaylistStorage()
  const { toast } = useToast()

  // Check if playlist exists in local storage
  const localPlaylist = getPlaylistById(playlistId)

  // Only fetch from API if:
  // 1. localStorage has finished loading, AND
  // 2. No playlist found in localStorage
  const shouldFetchFromAPI = !isLoadingStorage && !localPlaylist

  // If not in local storage, try to fetch from API
  const { data: fetchedPlaylist, isLoading: isLoadingAPI, error } = useFetchPlaylist(
    playlistId,
    shouldFetchFromAPI
  )

  // Use local playlist if available, otherwise use fetched playlist
  const playlist = localPlaylist || fetchedPlaylist

  // Auto-save fetched playlist to local storage
  useEffect(() => {
    if (fetchedPlaylist && !localPlaylist) {
      addSharedPlaylist(fetchedPlaylist)
        .then(() => {
          toast({
            title: "Playlist saved!",
            description: "This shared playlist has been added to your collection.",
            duration: 4000,
          })
        })
        .catch((err) => {
          console.error('Failed to auto-save playlist:', err)
          toast({
            title: "Auto-save failed",
            description: "Could not save the playlist automatically.",
            variant: "destructive",
            duration: 3000,
          })
        })
    }
  }, [fetchedPlaylist, localPlaylist, addSharedPlaylist, toast])

  if (isLoadingStorage || isLoadingAPI) {
    return (
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-2xl mx-auto text-center space-y-6">
          <h1 className="text-2xl font-bold">Loading Playlist...</h1>
          <p className="text-muted-foreground">
            Fetching playlist details from the server.
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

  // Determine track count - for fetched playlists use tracks array, for local use stored count
  const trackCount = 'trackCount' in playlist ? playlist.trackCount : playlist.tracks?.length || 0

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
        {fetchedPlaylist && localPlaylist && (
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
                    You can remove it anytime from your playlists page.
                  </p>
                </div>
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
                {'activity' in playlist ? playlist.activity : 'Shared Activity'}
              </Badge>
              <Badge className={`text-sm ${getVibeColor('vibe' in playlist ? playlist.vibe : 'mixed')}`}>
                {'vibe' in playlist ? playlist.vibe : 'mixed'}
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
              {fetchedPlaylist?.tracks ?
                'Detailed track information from the playlist.' :
                'Detailed track information will be available when connected to the full playlist data.'
              }
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Show actual tracks if we have them from the API */}
              {fetchedPlaylist?.tracks ? (
                fetchedPlaylist.tracks.map((track) => (
                  <div key={track.id} className="flex items-center gap-4 p-3 rounded-lg border">
                    <div className="w-12 h-12 bg-muted rounded-md flex items-center justify-center">
                      <Music className="w-5 h-5 text-muted-foreground" />
                    </div>
                    <div className="flex-1">
                      <div className="font-medium">{track.name}</div>
                      <div className="text-sm text-muted-foreground">{track.artist} • {track.album}</div>
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {Math.floor(track.duration / 60)}:
                      {String(track.duration % 60).padStart(2, '0')}
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
                ))
              ) : (
                /* Placeholder tracks for local playlists */
                Array.from({ length: trackCount }, (_, i) => (
                  <div key={i} className="flex items-center gap-4 p-3 rounded-lg border">
                    <div className="w-12 h-12 bg-muted rounded-md flex items-center justify-center">
                      <Music className="w-5 h-5 text-muted-foreground" />
                    </div>
                    <div className="flex-1">
                      <div className="font-medium">Track {i + 1}</div>
                      <div className="text-sm text-muted-foreground">Artist • Album</div>
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {Math.floor(Math.random() * 3) + 2}:
                      {String(Math.floor(Math.random() * 60)).padStart(2, '0')}
                    </div>
                  </div>
                ))
              )}
            </div>
            {!fetchedPlaylist?.tracks && (
              <div className="mt-6 text-center text-sm text-muted-foreground">
                <p>
                  💡 Full track details will be available when we implement detailed playlist fetching
                  from the backend.
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}