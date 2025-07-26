import { createFileRoute } from '@tanstack/react-router'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Music, ExternalLink, ArrowLeft } from 'lucide-react'
import { Link } from '@tanstack/react-router'
import { usePlaylistStorage } from '@/hooks/usePlaylistStorage'

export const Route = createFileRoute('/playlists/$playlistId')({
  component: PlaylistDetails,
})

function PlaylistDetails() {
  const { playlistId } = Route.useParams()
  const { getPlaylistById } = usePlaylistStorage()

  const playlist = getPlaylistById(playlistId)

  // TODO: If not in local storage, try to fetch from API
  // include "add playlist by ID" feature here once DB and backend routes exist
  if (!playlist) {
    return (
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-2xl mx-auto text-center space-y-6">
          <h1 className="text-2xl font-bold">Playlist Not Found</h1>
          <p className="text-muted-foreground">
            This playlist doesn't exist in your local collection.
          </p>
          {/* TODO: Add form to fetch playlist by ID from backend */}
          <div className="space-y-4">
            <p className="text-sm text-muted-foreground">
              If you have a playlist ID, you can try to load it:
            </p>
            <Button variant="outline" disabled>
              Load Playlist by ID (Coming Soon)
            </Button>
          </div>
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

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    } catch {
      return 'Unknown date'
    }
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

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex items-center gap-4">
          <Link to="/">
            <Button variant="outline" size="sm">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back
            </Button>
          </Link>
          <div className="flex-1">
            <h1 className="text-3xl font-bold">{playlist.name}</h1>
            <p className="text-muted-foreground mt-1">Created {formatDate(playlist.createdAt)}</p>
          </div>
        </div>

        {/* Playlist Overview */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-3">
              <Music className="w-6 h-6" />
              Playlist Details
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
              <Badge className={`text-sm ${getVibeColor(playlist.vibe)}`}>{playlist.vibe}</Badge>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
              <div className="space-y-1">
                <div className="text-2xl font-bold">{playlist.trackCount}</div>
                <div className="text-sm text-muted-foreground">Tracks</div>
              </div>
              <div className="space-y-1">
                <div className="text-2xl font-bold">{playlist.duration}</div>
                <div className="text-sm text-muted-foreground">Minutes</div>
              </div>
              <div className="space-y-1">
                <div className="text-2xl font-bold">
                  {Math.round(playlist.duration / playlist.trackCount)}
                </div>
                <div className="text-sm text-muted-foreground">Avg Track</div>
              </div>
              <div className="space-y-1">
                <div className="text-2xl font-bold">{playlist.vibe}</div>
                <div className="text-sm text-muted-foreground">Vibe</div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-3">
              <Button onClick={() => window.open(playlist.spotifyUrl, '_blank')} className="flex-1">
                <ExternalLink className="w-4 h-4 mr-2" />
                Open in Spotify
              </Button>
              <Button variant="outline">Share Playlist</Button>
            </div>
          </CardContent>
        </Card>

        {/* Track List Placeholder */}
        <Card>
          <CardHeader>
            <CardTitle>Track List</CardTitle>
            <CardDescription>
              Detailed track information will be available when connected to the full playlist data.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Placeholder for track list */}
              {Array.from({ length: playlist.trackCount }, (_, i) => (
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
              ))}
            </div>
            <div className="mt-6 text-center text-sm text-muted-foreground">
              <p>
                💡 Full track details will be available when we implement detailed playlist fetching
                from the backend.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
