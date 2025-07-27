// src/lib/constants.ts

export const PLAYLIST_VIBES = [
  { value: 'chill', label: 'Chill' },
  { value: 'upbeat', label: 'Upbeat' },
  { value: 'focus', label: 'Focus' },
  { value: 'energetic', label: 'Energetic' },
  { value: 'mellow', label: 'Mellow' },
  { value: 'ambient', label: 'Ambient' },
] as const

export type PlaylistVibe = (typeof PLAYLIST_VIBES)[number]['value']

// Helper function to get vibe colors consistently
export const getVibeColor = (vibe: string): string => {
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
