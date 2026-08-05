"""
ACT step of the agentic workflow.

Executes a Plan produced by planner.py, one discrete step at a time. Each
step is its own small, independently-loggable function (validate_input,
load_catalog, score_and_rank, format_output) rather than a single call that
does everything -- so a failure or a log line always points at exactly one
step, not "the recommender did something wrong somewhere".

This module only calls into the existing, unmodified recommender.py
(load_songs / recommend_songs) -- the agentic layer wraps that logic, it
doesn't replace it.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple

from .logger import get_logger
from .recommender import load_songs, recommend_songs

logger = get_logger()


class ActorError(Exception):
    """Raised when a plan step cannot be completed; carries which step failed."""


@dataclass
class ActorResult:
    preferences: Dict
    recommendations: List[Tuple[Dict, float, str]]
    formatted: List[Dict]
    used_full_catalog_fallback: bool


def validate_input(preferences: Dict) -> Dict:
    """
    Rejects malformed preferences before any scoring happens.

    Why: garbage in (missing keys, energy outside [0,1], non-string genre/
    mood) would otherwise surface as a confusing downstream KeyError/TypeError
    from inside the scoring loop instead of a clear, actionable message here.
    """
    logger.info("[ACT] validate_input: checking %s", preferences)

    required = ("genre", "mood", "energy")
    missing = [k for k in required if k not in preferences]
    if missing:
        raise ActorError(f"validate_input: missing required preference key(s): {missing}")

    genre, mood, energy = preferences["genre"], preferences["mood"], preferences["energy"]

    if not isinstance(genre, str) or not genre.strip():
        raise ActorError("validate_input: 'genre' must be a non-empty string")
    if not isinstance(mood, str) or not mood.strip():
        raise ActorError("validate_input: 'mood' must be a non-empty string")
    if not isinstance(energy, (int, float)) or not (0.0 <= float(energy) <= 1.0):
        raise ActorError(f"validate_input: 'energy' must be a number in [0, 1], got {energy!r}")

    normalized = {"genre": genre.strip(), "mood": mood.strip(), "energy": float(energy)}
    logger.info("[ACT] validate_input: OK -> %s", normalized)
    return normalized


def load_catalog(csv_path: str) -> List[Dict]:
    """
    Wraps recommender.load_songs with error handling.

    Why: a missing/renamed CSV or a corrupt row (bad float) is an
    environment problem, not a bug in the scoring logic -- it should fail
    with a clear message here rather than crash later during scoring.
    """
    logger.info("[ACT] load_catalog: reading %s", csv_path)

    try:
        songs = load_songs(csv_path)
    except FileNotFoundError as exc:
        raise ActorError(f"load_catalog: catalog file not found at {csv_path!r}") from exc
    except (ValueError, KeyError) as exc:
        raise ActorError(f"load_catalog: catalog file is malformed ({exc})") from exc

    if not songs:
        raise ActorError(f"load_catalog: catalog at {csv_path!r} loaded but contains zero songs")

    logger.info("[ACT] load_catalog: loaded %d songs", len(songs))
    return songs


def score_and_rank(preferences: Dict, songs: List[Dict], strategy: Dict) -> Tuple[List[Tuple[Dict, float, str]], bool]:
    """
    Scores and ranks songs per the plan's strategy.

    Why require_genre_match exists: a strict genre filter is a reasonable
    first attempt, but if the requested genre doesn't exist in the catalog
    it would silently return zero/near-zero-score results. Rather than
    let that pass through as "the answer", we fall back to scoring the
    full catalog (on mood/energy alone) and flag that we did so, so the
    Checker can factor it into its judgment.
    """
    k = strategy.get("k", 5)
    require_genre_match = strategy.get("require_genre_match", False)
    used_fallback = False

    candidate_songs = songs
    scoring_preferences = preferences

    if require_genre_match:
        filtered = [s for s in songs if s["genre"].lower() == preferences["genre"].lower()]
        if filtered:
            candidate_songs = filtered
            logger.info(
                "[ACT] score_and_rank: filtered catalog to %d songs matching genre=%s",
                len(filtered), preferences["genre"],
            )
        else:
            used_fallback = True
            logger.warning(
                "[ACT] score_and_rank: no songs match genre=%s; falling back to full catalog",
                preferences["genre"],
            )

    if not require_genre_match:
        # Relaxed strategy (either the planner's retry decision, or the
        # fallback branch above): scoring must ignore genre entirely, not
        # just widen the candidate pool. score_song() still awards a +2.0
        # genre bonus to any song whose genre happens to equal
        # preferences["genre"] -- left unchanged, a single strong genre
        # match (e.g. the catalog's one classical track) would keep
        # winning on every retry even though mood/energy are a poor fit,
        # which is exactly the failure this relaxed strategy exists to fix.
        scoring_preferences = {**preferences, "genre": ""}

    recommendations = recommend_songs(scoring_preferences, candidate_songs, k=k)
    logger.info("[ACT] score_and_rank: produced %d recommendation(s)", len(recommendations))
    return recommendations, used_fallback


def format_output(recommendations: List[Tuple[Dict, float, str]]) -> List[Dict]:
    """Converts raw (song, score, explanation) tuples into a display-ready list of dicts."""
    logger.info("[ACT] format_output: formatting %d recommendation(s)", len(recommendations))

    formatted = [
        {
            "title": song["title"],
            "artist": song["artist"],
            "genre": song["genre"],
            "mood": song["mood"],
            "score": round(score, 2),
            "explanation": explanation,
        }
        for song, score, explanation in recommendations
    ]
    return formatted


_STEP_FUNCTIONS = {
    "validate_input": validate_input,
    "load_catalog": load_catalog,
    "score_and_rank": score_and_rank,
    "format_output": format_output,
}


def execute_plan(plan, catalog_path: str = "data/songs.csv") -> ActorResult:
    """
    Runs the fixed validate -> load -> score -> format pipeline.

    The plan's step list is used for logging/traceability (what the
    Planner said it intended to do), but the actual call sequence is
    fixed here -- the Actor never dynamically executes arbitrary
    LLM-provided code, only these four known-safe functions.
    """
    step_names = [s["action"] for s in plan.steps]
    logger.info("[ACT] executing plan steps: %s", step_names)

    preferences = validate_input(plan.preferences)
    songs = load_catalog(catalog_path)
    recommendations, used_fallback = score_and_rank(preferences, songs, plan.strategy)
    formatted = format_output(recommendations)

    return ActorResult(
        preferences=preferences,
        recommendations=recommendations,
        formatted=formatted,
        used_full_catalog_fallback=used_fallback,
    )
