import { createFileRoute } from '@tanstack/react-router'
import { Music } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Link } from '@tanstack/react-router'
import { PlaylistGeneratorForm } from '@/components/PlaylistGeneratorForm'
import { PlaylistSummaryCard } from '@/components/PlaylistSummaryCard'
import { usePlaylistStorage } from '@/hooks/usePlaylistStorage'

export const Route = createFileRoute('/')({
  component: Index,
})

function Index() {
  const { removePlaylist, getRecentPlaylists, hasPlaylists } = usePlaylistStorage()
  const recentPlaylists = getRecentPlaylists(3)

  return (
    <div className="container mx-auto px-4 py-16">
      <div className="max-w-6xl mx-auto">
        {/* Hero Section */}
        <div className="text-center space-y-6 mb-12">
          <div className="flex justify-center">
            <Music className="h-16 w-16 text-primary" />
          </div>
          <h1 className="text-4xl font-bold tracking-tight lg:text-6xl">
            <span
              style={{
                background: 'linear-gradient(to right, #0ea5e9, #06b6d4)',
                WebkitBackgroundClip: 'text',
                backgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                color: 'transparent',
              }}
            >
              Fresh, perfectly timed Spotify playlists — made to match your moment.
            </span>
          </h1>
          <p className="text-xl leading-8 text-muted-foreground max-w-lg mx-auto">
          Just tell us what you’re doing, the kind of music you like, how long you’ll be at it, and the vibe you’re going for.
          </p>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column: Form */}
          <div className="lg:col-span-2">
            <PlaylistGeneratorForm />
          </div>

          {/* Right Column: Recent Playlists */}
          <div className="space-y-6">
            {hasPlaylists && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Your Recent Playlists</CardTitle>
                  <CardDescription>Your recently generated playlists</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {recentPlaylists.map(playlist => (
                    <PlaylistSummaryCard
                      key={playlist.id}
                      playlist={playlist}
                      onRemove={removePlaylist}
                      showRemoveButton={true}
                    />
                  ))}

                  <Link to="/playlists" className="block">
                      <Button
                        size="sm"
                        className="w-full bg-[#00378b] text-white hover:bg-[#002e73]"
                      >
                        View All Playlists ({recentPlaylists.length}+)
                      </Button>
                    </Link>
                </CardContent>
              </Card>
            )}

            {/* Info Card */}
            <Card>
              <CardContent className="pt-6">
                <div className="text-sm text-muted-foreground space-y-2">
                  <p>🎵 Your playlists are saved locally on this device</p>
                  <p>🔗 Share playlist links to sync across devices</p>
                  <p>✨ Each playlist is crafted based on your activity and vibe</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
