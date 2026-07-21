"""
Command line runner for the Music Recommender Simulation.

This file loads the song catalog, creates a sample user profile,
runs the recommender, and prints the top song recommendations.
"""

from .recommender import load_songs, recommend_songs


def main() -> None:
    # Load songs from the CSV file
    songs = load_songs("data/songs.csv")

    print(f"Loaded songs: {len(songs)}")

    # Sample user profile
    user_prefs = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
    }

    # Get top recommendations
    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\nTop Recommendations\n")
    print("-" * 50)

    for song, score, explanation in recommendations:
        print(f"🎵 {song['title']} by {song['artist']}")
        print(f"Genre: {song['genre']} | Mood: {song['mood']}")
        print(f"Score: {score:.2f}")
        print(f"Why: {explanation}")
        print("-" * 50)


if __name__ == "__main__":
    main()