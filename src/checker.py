"""
CHECK step of the agentic workflow.

Two layers, run in order:

1. Deterministic pre-check (fast, free, no network): catches structural
   problems -- empty results, out-of-range scores, duplicate songs, blank
   explanations, or a top score so low it indicates no real match. This
   layer runs on every attempt and never costs an API call.

2. LLM semantic check (only runs if layer 1 passes): judges whether the
   recommended songs actually satisfy what the user asked for in natural
   language -- something a fixed numeric threshold can't capture (e.g. the
   deterministic score looks fine but the songs are a mood mismatch the
   user would notice). Skipped gracefully if no LLM is available.

Both layers can trigger a retry; whichever layer fails is recorded so the
log makes clear which kind of decision blocked the output.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

from .actor import ActorResult
from .llm_client import call_llm_json
from .logger import get_logger

logger = get_logger()

MIN_ACCEPTABLE_SCORE = 1.2
MAX_POSSIBLE_SCORE = 4.01  # genre(2.0) + mood(1.0) + energy(<=1.0), with float slack

SYSTEM_PROMPT = """You are the quality-checking module of a music recommendation agent.
Given a user's original request and the songs recommended to them, judge
whether the recommendations reasonably satisfy the request.

Respond with ONLY a JSON object (no prose, no markdown fences):
{
  "passed": <bool>,
  "reason": <short string explaining the verdict>,
  "suggested_fix": {"reason": "low_score" | "wrong_mood" | "wrong_genre" | "none"}
}

Be pragmatic: a small catalog won't have a perfect match for every request.
Fail only if the results are clearly unrelated to what the user asked for.
"""


@dataclass
class CheckResult:
    passed: bool
    layer: str  # "deterministic" or "llm" or "skipped"
    reason: str
    suggested_fix: Optional[Dict] = None


def deterministic_check(user_request: str, actor_result: ActorResult) -> CheckResult:
    """Structural/statistical checks that require no external call."""
    recs = actor_result.recommendations

    if not recs:
        return CheckResult(False, "deterministic", "no recommendations produced",
                            {"reason": "low_score"})

    ids_seen = set()
    for song, score, explanation in recs:
        if song["id"] in ids_seen:
            return CheckResult(False, "deterministic", f"duplicate song id {song['id']} in results",
                                {"reason": "duplicate"})
        ids_seen.add(song["id"])

        if not (0.0 <= score <= MAX_POSSIBLE_SCORE):
            return CheckResult(False, "deterministic", f"score {score} out of expected range",
                                {"reason": "invalid_score"})

        if not explanation or not explanation.strip():
            return CheckResult(False, "deterministic", f"empty explanation for song id {song['id']}",
                                {"reason": "missing_explanation"})

    top_song, top_score, _ = recs[0]
    if top_score < MIN_ACCEPTABLE_SCORE:
        return CheckResult(
            False, "deterministic",
            f"top score {top_score:.2f} is below acceptable threshold {MIN_ACCEPTABLE_SCORE}"
            " (likely no strong genre/mood match)",
            {"reason": "low_score"},
        )

    # A genre match alone is worth +2.0, which can clear MIN_ACCEPTABLE_SCORE
    # even when the top result's mood and energy are both a poor fit (e.g. a
    # "happy, energetic" request landing on the catalog's one melancholy,
    # low-energy classical track just because the genre matches). Total
    # score is a poor proxy for relevance in that case, so mood/energy are
    # checked directly on the top result rather than trusting the sum.
    mood_match = top_song["mood"].lower() == actor_result.preferences["mood"].lower()
    energy_diff = abs(top_song["energy"] - actor_result.preferences["energy"])
    if not mood_match and energy_diff > 0.3:
        return CheckResult(
            False, "deterministic",
            f"top score {top_score:.2f} clears the threshold on genre match alone, but mood "
            f"({top_song['mood']!r} vs requested {actor_result.preferences['mood']!r}) and energy "
            f"(diff {energy_diff:.2f}) are both a poor fit",
            {"reason": "low_score"},
        )

    return CheckResult(True, "deterministic", f"structural checks passed, top score {top_score:.2f}")


def llm_semantic_check(user_request: str, actor_result: ActorResult) -> CheckResult:
    """
    Asks the LLM whether the results actually satisfy the request.

    Falls back to "skipped" (treated as passing) rather than blocking the
    whole pipeline when no LLM is available -- the deterministic layer has
    already verified structural correctness, so a missing LLM degrades the
    quality bar rather than breaking the run.
    """
    songs_summary = [
        {"title": f["title"], "genre": f["genre"], "mood": f["mood"], "score": f["score"]}
        for f in actor_result.formatted
    ]
    user_prompt = f"User request: {user_request!r}\nRecommended songs: {songs_summary}"

    result = call_llm_json(SYSTEM_PROMPT, user_prompt)

    if result is None or "passed" not in result:
        logger.info("[CHECK] llm_semantic_check: skipped (LLM unavailable or response unusable)")
        return CheckResult(True, "skipped", "LLM semantic check unavailable; deterministic pass stands")

    passed = bool(result["passed"])
    reason = result.get("reason", "")
    suggested_fix = result.get("suggested_fix")
    return CheckResult(passed, "llm", reason, suggested_fix if not passed else None)


def run_checks(user_request: str, actor_result: ActorResult) -> CheckResult:
    """Runs the deterministic layer first; only calls the LLM layer if that passes."""
    det = deterministic_check(user_request, actor_result)
    logger.info("[CHECK] (deterministic) passed=%s reason=%s", det.passed, det.reason)

    if not det.passed:
        return det

    llm_result = llm_semantic_check(user_request, actor_result)
    logger.info("[CHECK] (%s) passed=%s reason=%s", llm_result.layer, llm_result.passed, llm_result.reason)
    return llm_result
