import { createFileRoute } from '@tanstack/react-router'
import { useForm } from '@tanstack/react-form'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Music } from 'lucide-react'
import { useGeneratePlaylist } from '@/hooks/api/usePlaylist'

export const Route = createFileRoute('/')({
  component: Index,
})

// Type definitions for our form data
interface PlaylistFormData {
  activity: string
  duration: number
  vibe: string
}

function Index() {
  const generatePlaylistMutation = useGeneratePlaylist()

  const form = useForm({
    defaultValues: {
      activity: '',
      duration: 30,
      vibe: 'chill'
    } as PlaylistFormData,
    onSubmit: async ({ value }) => {
      try {
        const result = await generatePlaylistMutation.mutateAsync(value)

        // Success! Show the result or redirect to playlist view
        alert(`Playlist "${result.name}" created successfully!\nTracks: ${result.tracks.length}\nSpotify URL: ${result.spotifyUrl}`)

        // TODO: Later we can navigate to a playlist details page or show a success modal
        // navigate({ to: `/playlist/${result.id}` })

      } catch (error) {
        // Error handling is done in the mutation's onError callback
        // but you can also handle it here if needed
        console.error('Form submission error:', error)
      }
    }
  })

  return (
    <div className="container mx-auto px-4 py-16">
      <div className="max-w-2xl mx-auto">
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
              Nice Things
            </span>
          </h1>
          <p className="text-xl leading-8 text-muted-foreground max-w-lg mx-auto">
            Tell us what you're doing, how long you'll be doing it, and what vibe you want.
            We'll create the perfect Spotify playlist for you.
          </p>
        </div>

        {/* Playlist Generation Form */}
        <Card>
          <CardHeader>
            <CardTitle>Create Your Playlist</CardTitle>
            <CardDescription>
              Just fill in a few details and we'll curate the perfect soundtrack for your activity.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form
              onSubmit={(e) => {
                e.preventDefault()
                e.stopPropagation()
                void form.handleSubmit()
              }}
              className="space-y-6"
            >
              {/* Activity Input */}
              <form.Field
                name="activity"
                validators={{
                  onChange: ({ value }) =>
                    !value?.trim() ? 'Activity is required' : undefined,
                }}
              >
                {(field) => (
                  <div className="space-y-2">
                    <Label htmlFor={field.name}>What are you doing?</Label>
                    <Input
                      id={field.name}
                      name={field.name}
                      value={field.state.value}
                      onBlur={field.handleBlur}
                      onChange={(e) => field.handleChange(e.target.value)}
                      placeholder="e.g., yoga, studying, cleaning, cooking..."
                    />
                    {field.state.meta.errors.length > 0 && (
                      <p className="text-sm text-destructive">
                        {field.state.meta.errors[0]}
                      </p>
                    )}
                  </div>
                )}
              </form.Field>

              {/* Duration Input */}
              <form.Field
                name="duration"
                validators={{
                  onChange: ({ value }) => {
                    if (!value || value < 5) return 'Duration must be at least 5 minutes'
                    if (value > 300) return 'Duration cannot exceed 300 minutes'
                    return undefined
                  },
                }}
              >
                {(field) => (
                  <div className="space-y-2">
                    <Label htmlFor={field.name}>How long? (minutes)</Label>
                    <Input
                      id={field.name}
                      name={field.name}
                      type="number"
                      min="5"
                      max="300"
                      value={field.state.value}
                      onBlur={field.handleBlur}
                      onChange={(e) => field.handleChange(parseInt(e.target.value) || 5)}
                    />
                    {field.state.meta.errors.length > 0 && (
                      <p className="text-sm text-destructive">
                        {field.state.meta.errors[0]}
                      </p>
                    )}
                  </div>
                )}
              </form.Field>

              {/* Vibe Selection */}
              <form.Field
                name="vibe"
                validators={{
                  onChange: ({ value }) =>
                    !value ? 'Please select a vibe' : undefined,
                }}
              >
                {(field) => (
                  <div className="space-y-2">
                    <Label htmlFor={field.name}>What's the vibe?</Label>
                    <select
                      id={field.name}
                      name={field.name}
                      value={field.state.value}
                      onBlur={field.handleBlur}
                      onChange={(e) => field.handleChange(e.target.value)}
                      className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      <option value="chill">Chill</option>
                      <option value="upbeat">Upbeat</option>
                      <option value="focus">Focus</option>
                      <option value="energetic">Energetic</option>
                      <option value="mellow">Mellow</option>
                      <option value="ambient">Ambient</option>
                    </select>
                    {field.state.meta.errors.length > 0 && (
                      <p className="text-sm text-destructive">
                        {field.state.meta.errors[0]}
                      </p>
                    )}
                  </div>
                )}
              </form.Field>

              {/* Submit Button */}
              <form.Subscribe
                selector={(state) => [state.canSubmit, state.isSubmitting]}
              >
                {([canSubmit, isSubmitting]) => (
                  <Button
                    type="submit"
                    className="w-full"
                    disabled={!canSubmit || generatePlaylistMutation.isPending}
                  >
                    {generatePlaylistMutation.isPending || isSubmitting
                      ? 'Generating Your Playlist...'
                      : 'Generate Playlist'
                    }
                  </Button>
                )}
              </form.Subscribe>

              {/* Error Display */}
              {generatePlaylistMutation.isError && (
                <div className="text-sm text-destructive text-center">
                  {generatePlaylistMutation.error?.message || 'Failed to generate playlist. Please try again.'}
                </div>
              )}
            </form>
          </CardContent>
        </Card>

        {/* Additional Info */}
        <div className="mt-8 text-center text-sm text-muted-foreground">
          <p>
            Your playlist will be created and saved to your Spotify account.
            We'll use your preferences to find the perfect songs for your activity.
          </p>
        </div>
      </div>
    </div>
  )
}