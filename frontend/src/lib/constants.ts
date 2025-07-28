// src/lib/constants.ts

export const VIBE_CATEGORIES = {
  'Relaxation': [
    { value: 'chill', label: 'Chill' },
    { value: 'mellow', label: 'Mellow' },
    { value: 'peaceful', label: 'Peaceful' },
    { value: 'calm', label: 'Calm' },
    { value: 'relaxed', label: 'Relaxed' },
  ],
  'Focus & Flow': [
    { value: 'moderate', label: 'Moderate' },
    { value: 'steady', label: 'Steady' },
    { value: 'focused', label: 'Focused' },
    { value: 'balanced', label: 'Balanced' },
  ],
  'High Energy': [
    { value: 'energetic', label: 'Energetic' },
    { value: 'upbeat', label: 'Upbeat' },
    { value: 'intense', label: 'Intense' },
    { value: 'pumped', label: 'Pumped' },
    { value: 'aggressive', label: 'Aggressive' },
    { value: 'powerful', label: 'Powerful' },
  ],
  'Mood & Emotion': [
    { value: 'happy', label: 'Happy' },
    { value: 'uplifting', label: 'Uplifting' },
    { value: 'motivational', label: 'Motivational' },
    { value: 'inspiring', label: 'Inspiring' },
    { value: 'dark', label: 'Dark' },
    { value: 'melancholy', label: 'Melancholy' },
  ],
};

export const PLAYLIST_VIBES = Object.values(VIBE_CATEGORIES).flat();

export type PlaylistVibe = (typeof PLAYLIST_VIBES)[number]['value']

// Helper function to get vibe colors consistently
export const getVibeColor = (vibe: string): string => {
  const colors: Record<string, string> = {
    // Relaxation
    chill: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    mellow: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
    peaceful: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    calm: 'bg-teal-100 text-teal-800 dark:bg-teal-900 dark:text-teal-200',
    relaxed: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200',

    // Focus & Flow
    moderate: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200',
    steady: 'bg-gray-200 text-gray-800 dark:bg-gray-600 dark:text-gray-100',
    focused: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    balanced: 'bg-gray-300 text-gray-800 dark:bg-gray-500 dark:text-gray-100',

    // High Energy
    energetic: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
    upbeat: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
    intense: 'bg-rose-100 text-rose-800 dark:bg-rose-900 dark:text-rose-200',
    pumped: 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200',
    aggressive: 'bg-red-200 text-red-900 dark:bg-red-800 dark:text-red-100',
    powerful: 'bg-red-300 text-red-900 dark:bg-red-700 dark:text-red-100',

    // Mood & Emotion
    happy: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    uplifting: 'bg-sky-100 text-sky-800 dark:bg-sky-900 dark:text-sky-200',
    motivational: 'bg-cyan-100 text-cyan-800 dark:bg-cyan-900 dark:text-cyan-200',
    inspiring: 'bg-lime-100 text-lime-800 dark:bg-lime-900 dark:text-lime-200',
    dark: 'bg-gray-800 text-gray-200 dark:bg-gray-900 dark:text-gray-100',
    melancholy: 'bg-blue-200 text-blue-900 dark:bg-blue-800 dark:text-blue-100',
  }
  return colors[vibe.toLowerCase()] || colors.chill
}
