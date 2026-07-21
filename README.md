# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Explain your design in plain language.

Some prompts to answer:

- What features does each `Song` use in your system
  - For example: genre, mood, energy, tempo
- What information does your `UserProfile` store
- How does your `Recommender` compute a score for each song
- How do you choose which songs to recommend

You can include a simple diagram or bullet list if helpful.

Claude finished the response
Synthesized documentation framework for recommendation system overview
Synthesized documentation framework for recommendation system overview

Here's a draft for the How The System Works section of your README. Since this needs to reflect your understanding, treat this as a starting point — tweak the wording so it sounds like you, and adjust priorities if you disagree with the weighting choices.

How The System Works

Real-world music platforms like Spotify and YouTube generally combine two approaches to predict what a user will love next. Collaborative filtering looks at patterns across many users — if listeners with similar histories to you enjoyed a song, it gets recommended to you too, regardless of what the song actually sounds like. Content-based filtering instead looks at the attributes of the songs themselves — genre, tempo, energy, mood — and compares them against a profile of what a specific user tends to prefer. Large-scale systems blend both, along with implicit signals like skips, replays, and listening duration, to constantly refine their predictions. This project simulates the content-based half of that process: rather than learning from crowd behavior, it builds a UserProfile representing a listener's preferences and scores each Song in the catalog by how closely its attributes match that profile.

My version prioritizes energy and mood/valence over strict genre matching, because a listener's "vibe" in the moment (e.g., wanting something chill or something intense) tends to predict enjoyment better than genre alone — two songs in different genres can feel more similar than two songs in the same genre. Genre and secondary attributes like danceability and acousticness are used as supporting signals rather than the primary driver of a recommendation. The system separates scoring (how well one song matches the profile) from ranking (how the full list of scored songs gets ordered and presented), which will let me later experiment with ranking strategies — like injecting variety — without changing the underlying scoring logic.

Features used by Song:

genre (categorical)
mood (categorical)
energy (numerical, 0–1)
tempo_bpm (numerical)
valence (numerical, 0–1)
danceability (numerical, 0–1)
acousticness (numerical, 0–1)

Features used by UserProfile:

preferred_genre
preferred_mood
preferred_energy (target value, 0–1)
preferred_tempo_bpm (target value)
preferred_valence (target value, 0–1)
optionally: preferred_danceability, preferred_acousticness for later refinement

A couple of things worth doing before you paste this in:

Decide if you actually want UserProfile to store target values (e.g. "I like energy around 0.5") vs. a liked songs list it derives preferences from — both are valid designs, and it changes how Phase 3 implementation goes.
Make sure the paragraph reflects your own reasoning from Step 3 (if you ended up weighting genre higher than mood, flip the emphasis).

Want help sketching out the actual Song and UserProfile class skeletons next, or are you waiting until Phase 3 for that? And whenever you have it, go ahead and paste Phase 2 — I want to make sure the design phase lines up with what you write here.

remoce all emdashes btw

Recognized meta-instruction; declined to process formatting directive
Recognized meta-instruction; declined to process formatting directive

Here's the revised version with all em-dashes removed:

How The System Works

Real-world music platforms like Spotify and YouTube generally combine two approaches to predict what a user will love next. Collaborative filtering looks at patterns across many users: if listeners with similar histories to you enjoyed a song, it gets recommended to you too, regardless of what the song actually sounds like. Content-based filtering instead looks at the attributes of the songs themselves, such as genre, tempo, energy, and mood, and compares them against a profile of what a specific user tends to prefer. Large-scale systems blend both approaches, along with implicit signals like skips, replays, and listening duration, to constantly refine their predictions. This project simulates the content-based half of that process. Rather than learning from crowd behavior, it builds a UserProfile representing a listener's preferences and scores each Song in the catalog by how closely its attributes match that profile.

My version prioritizes energy and mood/valence over strict genre matching, because a listener's "vibe" in the moment (wanting something chill or something intense, for example) tends to predict enjoyment better than genre alone. Two songs in different genres can feel more similar than two songs in the same genre. Genre and secondary attributes like danceability and acousticness are used as supporting signals rather than the primary driver of a recommendation. The system separates scoring (how well one song matches the profile) from ranking (how the full list of scored songs gets ordered and presented). This separation will let me later experiment with ranking strategies, like injecting variety, without changing the underlying scoring logic.

Features used by Song:

genre (categorical)
mood (categorical)
energy (numerical, 0 to 1)
tempo_bpm (numerical)
valence (numerical, 0 to 1)
danceability (numerical, 0 to 1)
acousticness (numerical, 0 to 1)

Features used by UserProfile:

preferred_genre
preferred_mood
preferred_energy (target value, 0 to 1)
preferred_tempo_bpm (target value)
preferred_valence (target value, 0 to 1)
optionally: preferred_danceability, preferred_acousticness for later refinement

### User Profile (planned)

\`\`\`python
user_profile = {
    "favorite_genre": "lofi",
    "favorite_mood": "chill",
    "target_energy": 0.40,
    "target_valence": 0.60,
    "target_tempo_bpm": 80,
    "target_danceability": 0.55,
}
\`\`\`

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

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

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



