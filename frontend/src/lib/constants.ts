// src/lib/constants.ts

export const PLAYLIST_VIBES = [
  { value: 'ambient', label: 'Ambient Flow: 30–50 BPM' },
  { value: 'chill', label: 'Chill & Easy: 50–70 BPM' },
  { value: 'mellow', label: 'Mellow Movement: 70–90 BPM' },
  { value: 'focus', label: 'Steady Focus: 90–110 BPM' },
  { value: 'feel_good', label: 'Feel Good Energy: 110–140 BPM' },
  { value: 'high_energy', label: 'High Intensity: 140+ BPM' },
] as const


export type PlaylistVibe = (typeof PLAYLIST_VIBES)[number]['value']

// Helper function to get vibe colors consistently
export const getVibeColor = (vibe: string): string => {
  const colors: Record<string, string> = {
    ambient: 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200',
    chill: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    mellow: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
    focus: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    feel_good: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    high_energy: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  }
  return colors[vibe.toLowerCase()] || colors.chill
}

