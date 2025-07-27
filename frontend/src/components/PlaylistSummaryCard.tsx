import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Music, Clock, ExternalLink, Trash2 } from 'lucide-react'
import { Link } from '@tanstack/react-router'
import type { StoredPlaylist } from '@/hooks/usePlaylistStorage'
import { getVibeColor } from '@/lib/constants.ts'

interface PlaylistSummaryCardProps {
  playlist: StoredPlaylist
  onRemove?: (id: string) => void
  showRemoveButton?: boolean
}

export const PlaylistSummaryCard = ({
                                      playlist,
                                      onRemove,
                                      showRemoveButton = false,
                                    }: PlaylistSummaryCardProps) => {
  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    } catch {
      return 'Unknown date'
    }
  }

  // Get track count from tracks array length, fall back to trackCount for backwards compatibility
  const trackCount = playlist.tracks?.length ?? (playlist as any).trackCount ?? 0

  return (
      <Card className="hover:shadow-md transition-shadow duration-200">
        {playlist.imageUrl && (
            <img
                src={playlist.imageUrl}
                alt={`Cover for ${playlist.name}`}
                className="w-full h-48 object-cover rounded-t-lg"
                onError={e => {
                  e.currentTarget.src = 'https://via.placeholder.com/300x300.png?text=Playlist+Image' // Fallback image
                }}
            />
        )}
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="space-y-1 flex-1">
              <CardTitle className="text-lg leading-tight">{playlist.name}</CardTitle>
              <CardDescription className="text-sm">{playlist.description}</CardDescription>
            </div>
            {showRemoveButton && onRemove && (
                <Button
                    variant="ghost"
                    size="sm"
                    onClick={e => {
                      e.preventDefault()
                      onRemove(playlist.id)
                    }}
                    className="ml-2 h-8 w-8 p-0 text-muted-foreground hover:text-destructive"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
            )}
          </div>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="space-y-3">
            {/* Activity and Vibe Badges */}
            <div className="flex flex-wrap gap-2">
              <Badge variant="secondary" className="text-xs">
                <Music className="w-3 h-3 mr-1" />
                {playlist.activity}
              </Badge>
              <Badge className={`text-xs ${getVibeColor(playlist.vibe)}`}>{playlist.vibe}</Badge>
            </div>

            {/* Duration and Track Count */}
            <div className="flex items-center justify-between text-sm text-muted-foreground">
              <div className="flex items-center gap-4">
              <span className="flex items-center gap-1">
                <Clock className="w-4 h-4" />
                {playlist.duration} min
              </span>
                <span>{trackCount} tracks</span>
              </div>
              <span className="text-xs">{formatDate(playlist.createdAt)}</span>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-2">
              <Link
                  to="/playlists/$playlistId"
                  params={{ playlistId: playlist.id }}
                  className="flex-1"
              >
                <Button variant="outline" size="sm" className="w-full">
                  View Details
                </Button>
              </Link>
              <Button
                  variant="outline"
                  size="sm"
                  onClick={e => {
                    e.preventDefault()
                    window.open(playlist.spotifyUrl, '_blank')
                  }}
                  className="px-3"
              >
                <ExternalLink className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
  )
}