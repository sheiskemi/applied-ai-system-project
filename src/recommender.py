import csv
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        scored_songs = []

        for song in self.songs:
            score = 0

            if song.genre.lower() == user.favorite_genre.lower():
                score += 2.0

            if song.mood.lower() == user.favorite_mood.lower():
                score += 1.0

            score += max(0, 1 - abs(song.energy - user.target_energy))

            if user.likes_acoustic:
                score += song.acousticness
            else:
                score += 1 - song.acousticness

            scored_songs.append((score, song))

        scored_songs.sort(key=lambda x: x[0], reverse=True)

        return [song for score, song in scored_songs[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        reasons = []

        if song.genre.lower() == user.favorite_genre.lower():
            reasons.append("genre match")

        if song.mood.lower() == user.favorite_mood.lower():
            reasons.append("mood match")

        if abs(song.energy - user.target_energy) <= 0.2:
            reasons.append("similar energy")

        if user.likes_acoustic and song.acousticness >= 0.5:
            reasons.append("matches acoustic preference")

        return ", ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """

    songs = []

    with open(csv_path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            row["id"] = int(row["id"])
            row["energy"] = float(row["energy"])
            row["tempo_bpm"] = float(row["tempo_bpm"])
            row["valence"] = float(row["valence"])
            row["danceability"] = float(row["danceability"])
            row["acousticness"] = float(row["acousticness"])

            songs.append(row)

    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    """

    score = 0.0
    reasons = []

    # Genre match
    if song["genre"].lower() == user_prefs["genre"].lower():
        score += 2.0
        reasons.append("Genre match (+2.0)")

    # Mood match
    if song["mood"].lower() == user_prefs["mood"].lower():
        score += 1.0
        reasons.append("Mood match (+1.0)")

    # Energy similarity
    energy_score = max(0, 1 - abs(song["energy"] - user_prefs["energy"]))
    score += energy_score
    reasons.append(f"Energy similarity (+{energy_score:.2f})")

    return score, reasons


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """

    recommendations = []

    for song in songs:
        score, reasons = score_song(user_prefs, song)

        recommendations.append(
            (
                song,
                score,
                ", ".join(reasons),
            )
        )

    recommendations.sort(key=lambda x: x[1], reverse=True)

    return recommendations[:k]