# 🎵 Music Recommender Simulation

## Project Summary

This project is a simple content-based music recommender system built in Python. It recommends songs by comparing a user's preferred genre, mood, and energy level with the attributes of songs in a small music catalog. Each song receives a score based on how closely it matches the user's preferences, and the highest scoring songs are recommended along with a short explanation of why they were selected.

---

## How the System Works

This recommender uses a content-based approach. Instead of learning from other users, it compares the characteristics of each song with the user's preferences.

### Song Features

Each song includes the following information:

- Genre
- Mood
- Energy
- Tempo
- Valence
- Danceability
- Acousticness

### User Profile

The user provides:

- Preferred genre
- Preferred mood
- Preferred energy level

### Scoring Process

Each song is scored using three features:

- A matching genre receives **2 points**.
- A matching mood receives **1 point**.
- Songs with an energy level closer to the user's preferred energy receive a higher score.

After every song has been scored, the songs are sorted from highest to lowest score, and the top recommendations are returned with an explanation showing why each song was recommended.

---

## Getting Started

### Setup

1. (Optional) Create a virtual environment.

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Mac/Linux:

```bash
source .venv/bin/activate
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Run the program.

```bash
python -m src.main
```

---

## Running Tests

Run the tests with:

```bash
pytest
```

---

## Sample Recommendation Output

```text
Loaded songs: 18

Top Recommendations

--------------------------------------------------
🎵 Sunrise City by Neon Echo
Genre: pop | Mood: happy
Score: 3.98
Why: Genre match (+2.0), Mood match (+1.0), Energy similarity (+0.98)
--------------------------------------------------
🎵 Gym Hero by Max Pulse
Genre: pop | Mood: intense
Score: 2.87
Why: Genre match (+2.0), Energy similarity (+0.87)
--------------------------------------------------
🎵 Rooftop Lights by Indigo Parade
Genre: indie pop | Mood: happy
Score: 1.96
Why: Mood match (+1.0), Energy similarity (+0.96)
--------------------------------------------------
🎵 Night Drive Loop by Neon Echo
Genre: synthwave | Mood: moody
Score: 0.95
Why: Energy similarity (+0.95)
--------------------------------------------------
🎵 Storm Runner by Voltline
Genre: rock | Mood: intense
Score: 0.89
Why: Energy similarity (+0.89)
--------------------------------------------------
```

---

## Experiments

I tested the recommender using several different user profiles, including High Energy Pop, Chill Lofi, Deep Intense Rock, and a Happy Classical Fan. Each profile produced different recommendations based on the selected preferences.

I also experimented with the scoring algorithm by reducing the genre weight from **2.0** to **1.0** and doubling the importance of energy. After making this change, songs with energy levels closer to the user's preferred energy ranked higher, even when they belonged to a different genre. This demonstrated how changing feature weights directly affects recommendation results.

---

## Limitations and Risks

This recommender only uses genre, mood, and energy when scoring songs. It does not consider tempo, lyrics, listening history, or user feedback. Because the dataset contains only 18 songs, the same recommendations may appear for different users. The algorithm also depends on exact genre and mood matches, so similar songs with different labels may receive lower scores.

---

## Reflection

This project helped me understand how recommendation systems use user preferences and item features to make personalized suggestions. I learned that even a simple scoring algorithm can produce recommendations that feel relevant when the right features are chosen.

I also learned that recommendation systems have limitations. Small datasets and simple scoring rules can introduce bias and reduce recommendation diversity. Testing different user profiles and changing the scoring weights showed how small changes in the algorithm can significantly affect the recommendations.