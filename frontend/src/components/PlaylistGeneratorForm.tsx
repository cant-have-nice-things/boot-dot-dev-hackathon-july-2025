// src/components/PlaylistGeneratorForm.tsx
import { useForm } from '@tanstack/react-form'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Slider } from '@/components/ui/slider'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useGeneratePlaylist } from '@/hooks/api/usePlaylist'
import { usePlaylistStorage } from '@/hooks/usePlaylistStorage'
import { PLAYLIST_VIBES } from '@/lib/constants'

interface PlaylistFormData {
  activity: string
  duration: number
  vibe: string
}

interface PlaylistGeneratorFormProps {
  onPlaylistGenerated?: () => void
}

export const PlaylistGeneratorForm = ({ onPlaylistGenerated }: PlaylistGeneratorFormProps) => {
  const generatePlaylistMutation = useGeneratePlaylist()
  const { addPlaylist } = usePlaylistStorage()

  const form = useForm({
    defaultValues: {
      activity: '',
      duration: 30,
      vibe: PLAYLIST_VIBES[0].value,
    } as PlaylistFormData,
    onSubmit: async ({ value }) => {
      try {
        const result = await generatePlaylistMutation.mutateAsync(value)

        // Add to local storage
        addPlaylist(result, { activity: value.activity, vibe: value.vibe })

        // Reset form after successful submission
        form.reset()

        // Optional callback for parent component
        onPlaylistGenerated?.()

        console.log('Playlist added to your collection!')
      } catch (error) {
        console.error('Form submission error:', error)
      }
    },
  })

  return (
    <Card>
      <CardHeader>
        <CardTitle>Create Your Playlist</CardTitle>
        <CardDescription>
        Tell us what you're up to, how long you're doing it, and the vibe you're feeling. Finally pick your favorite music style.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form
          onSubmit={e => {
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
              onChange: ({ value }) => (!value?.trim() ? 'Please enter an activity' : undefined),
            }}
          >
            {field => (
              <div className="space-y-2">
                <Label htmlFor={field.name}>What activity are you doing & the type of music?</Label>
                <Input
                  id={field.name}
                  name={field.name}
                  value={field.state.value}
                  onBlur={field.handleBlur}
                  onChange={e => field.handleChange(e.target.value)}
                  placeholder="eg.. running with eletronic, coding with classical, cooking with EDM."
                  className="w-full"
                />
                {field.state.meta.errors.length > 0 && (
                  <p className="text-sm text-destructive">{field.state.meta.errors[0]}</p>
                )}
              </div>
            )}
          </form.Field>

          {/* Duration Slider */}
          <form.Field name="duration">
            {field => (
              <div className="space-y-3">
                <Label htmlFor={field.name}>Duration: {field.state.value} minutes</Label>
                <Slider
                  id={field.name}
                  min={10}
                  max={1440}
                  step={5}
                  value={[field.state.value]}
                  onValueChange={values => field.handleChange(values[0])}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>10 min</span>
                  <span>3 hours</span>
                </div>
              </div>
            )}
          </form.Field>

          {/* Vibe Selection */}
          <form.Field
            name="vibe"
            validators={{
              onChange: ({ value }) => (!value?.trim() ? 'Please select a vibe' : undefined),
            }}
          >
            {field => (
              <div className="space-y-2">
                <Label htmlFor={field.name}>What's the vibe?</Label>
                <select
                  id={field.name}
                  name={field.name}
                  value={field.state.value}
                  onBlur={field.handleBlur}
                  onChange={e => field.handleChange(e.target.value)}
                  className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {PLAYLIST_VIBES.map(vibe => (
                    <option key={vibe.value} value={vibe.value}>
                      {vibe.label}
                    </option>
                  ))}
                </select>
                {field.state.meta.errors.length > 0 && (
                  <p className="text-sm text-destructive">{field.state.meta.errors[0]}</p>
                )}
              </div>
            )}
          </form.Field>

          {/* Submit Button */}
          <form.Subscribe selector={state => [state.canSubmit, state.isSubmitting]}>
            {([canSubmit, isSubmitting]) => (
              <Button
                type="submit"
                className="w-full"
                disabled={!canSubmit || generatePlaylistMutation.isPending}
              >
                {generatePlaylistMutation.isPending || isSubmitting
                  ? 'Generating Your Playlist...'
                  : 'Generate Playlist'}
              </Button>
            )}
          </form.Subscribe>

          {/* Error Display */}
          {generatePlaylistMutation.isError && (
            <div className="text-sm text-destructive text-center">
              {generatePlaylistMutation.error?.message ||
                'Failed to generate playlist. Please try again.'}
            </div>
          )}
        </form>
      </CardContent>
    </Card>
  )
}
