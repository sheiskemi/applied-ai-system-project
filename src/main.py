"""
Command line runner for the Music Recommender Simulation.

This file loads the song catalog, creates multiple sample user profiles,
runs the recommender, and prints the top song recommendations.
"""

from .recommender import load_songs, recommend_songs


def main() -> None:
    # Load songs from the CSV file
    songs = load_songs("data/songs.csv")

    print(f"Loaded songs: {len(songs)}")

    # Test profiles
    profiles = [
        {
            "name": "High-Energy Pop",
            "prefs": {
                "genre": "pop",
                "mood": "happy",
                "energy": 0.9,
            },
        },
        {
            "name": "Chill Lofi",
            "prefs": {
                "genre": "lofi",
                "mood": "chill",
                "energy": 0.3,
            },
        },
        {
            "name": "Deep Intense Rock",
            "prefs": {
                "genre": "rock",
                "mood": "intense",
                "energy": 0.95,
            },
        },
        {
            "name": "Edge Case: Happy Classical Fan",
            "prefs": {
                "genre": "classical",
                "mood": "happy",
                "energy": 0.95,
            },
        },
    ]

    # Run recommendations for each profile
    for profile in profiles:
        print("\n" + "=" * 60)
        print(f"Profile: {profile['name']}")
        print("=" * 60)

        recommendations = recommend_songs(profile["prefs"], songs, k=5)

        for song, score, explanation in recommendations:
            print(f"🎵 {song['title']} by {song['artist']}")
            print(f"Genre: {song['genre']} | Mood: {song['mood']}")
            print(f"Score: {score:.2f}")
            print(f"Why: {explanation}")
            print("-" * 60)


if __name__ == "__main__":
    main()