import { createFileRoute } from '@tanstack/react-router'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ArrowLeft, Search, Music } from 'lucide-react'
import { Link } from '@tanstack/react-router'
import { PlaylistSummaryCard } from '@/components/PlaylistSummaryCard'
import { usePlaylistStorage } from '@/hooks/usePlaylistStorage'
import { useState } from 'react'

export const Route = createFileRoute('/playlists/')({
  component: PlaylistsIndex,
})

function PlaylistsIndex() {
  const { playlists, removePlaylist, hasPlaylists } = usePlaylistStorage()
  const [searchTerm, setSearchTerm] = useState('')

  // Filter playlists based on search term
  const filteredPlaylists = playlists.filter(
    playlist =>
      playlist.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      playlist.activity.toLowerCase().includes(searchTerm.toLowerCase()) ||
      playlist.vibe.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex items-center gap-4">
          <Link to="/">
            <Button variant="outline" size="sm">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Generator
            </Button>
          </Link>
          <div className="flex-1">
            <h1 className="text-3xl font-bold">Your Playlists</h1>
            <p className="text-muted-foreground mt-1">
              {hasPlaylists
                ? `${playlists.length} playlist${playlists.length === 1 ? '' : 's'} in your collection`
                : 'No playlists yet'}
            </p>
          </div>
        </div>

        {hasPlaylists ? (
          <>
            {/* Search */}
            <Card>
              <CardContent className="pt-6">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
                  <Input
                    placeholder="Search by name, activity, or vibe..."
                    value={searchTerm}
                    onChange={e => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </CardContent>
            </Card>

            {/* Playlists Grid */}
            {filteredPlaylists.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredPlaylists.map(playlist => (
                  <PlaylistSummaryCard
                    key={playlist.id}
                    playlist={playlist}
                    onRemove={removePlaylist}
                    showRemoveButton={true}
                  />
                ))}
              </div>
            ) : (
              <Card>
                <CardContent className="py-12 text-center">
                  <Search className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-medium mb-2">No playlists found</h3>
                  <p className="text-muted-foreground mb-4">
                    No playlists match your search for "{searchTerm}"
                  </p>
                  <Button variant="outline" onClick={() => setSearchTerm('')}>
                    Clear Search
                  </Button>
                </CardContent>
              </Card>
            )}
          </>
        ) : (
          /* Empty State */
          <Card>
            <CardContent className="py-16 text-center">
              <Music className="w-16 h-16 text-muted-foreground mx-auto mb-6" />
              <h2 className="text-2xl font-bold mb-4">No Playlists Yet</h2>
              <p className="text-muted-foreground mb-8 max-w-md mx-auto">
                You haven't generated any playlists yet. Create your first playlist to get started!
              </p>
              <Link to="/">
                <Button>
                  <Music className="w-4 h-4 mr-2" />
                  Create Your First Playlist
                </Button>
              </Link>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
