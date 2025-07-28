Danny To Do: 

Frontend:
[ ] Upload new hero image 1:1 Ratio. 
[ ] Make gap slighlty smaller above "What are you up to?"
[ ] Add extra key/value "Music Genre" category + constants. Key/values {Pop, Hip-Hop, Electronic, Lo-fi, Rock, R&B, Reggaeton, Jazz, Classical, Country, Afrobeats, Indie}
    * Possibly in @constants  
        export const PLAYLIST_VIBES = [
            { value: 'pop', label: 'Pop – Catchy and upbeat' },
            { value: 'hiphop', label: 'Hip-Hop – Rhythmic and lyrical' },
            { value: 'electronic', label: 'Electronic – Danceable and high-energy' },
            { value: 'lofi', label: 'Lo-fi – Chill and mellow' },
            { value: 'rock', label: 'Rock – Guitar-driven and bold' },
            { value: 'rnb', label: 'R&B – Smooth and soulful' },
            { value: 'reggaeton', label: 'Reggaeton – Latin beats and rhythm' },
            { value: 'jazz', label: 'Jazz – Sophisticated and expressive' },
            { value: 'classical', label: 'Classical – Orchestral and cinematic' },
            { value: 'country', label: 'Country – Acoustic and storytelling' },
            { value: 'afrobeats', label: 'Afrobeats – Rhythmic and energetic' },
            { value: 'indie', label: 'Indie – Alternative' }
        ] as const

      Minor Impormvents. If time.  
[ ] Make gap slighlty smaller above "What are you up to?"
[ ] New Advanced Controls. Add an expand to show extra features. Just more of the slider kind of features:
    Here are a bunch of option to choose from.  - All reference here "https://reccobeats.com/docs/apis/get-track-audio-features"
    * Possilby in @constants?


                    export const AUDIO_FEATURE_CONTROLS = {
                acousticness: {
                    label: 'Acousticness',
                    range: [0, 1],
                },
                danceability: {
                    label: 'Danceability',
                    range: [0, 1],
                },
                energy: {
                    label: 'Energy',
                    range: [0, 1],
                },
                instrumentalness: {
                    label: 'Instrumentalness',
                    range: [0, 1],
                },
                liveness: {
                    label: 'Liveness',
                    range: [0, 1],
                },
                loudness: {
                    label: 'Loudness (dB)',
                    range: [-60, 0],
                },
                speechiness: {
                    label: 'Speechiness',
                    range: [0, 1],
                },
                tempo: {
                    label: 'Tempo (BPM)',
                    range: [50, 250],
                },
                valence: {
                    label: 'Valence (Mood)',
                    range: [0, 1],
                },
                } as const



                
               

[ ]
[ ]
[ ]


Mike to do
[ ] 
[ ]
[ ]
[ ]
[ ]
[ ]

