"""
Orchestrator for the agentic workflow: Plan -> Act -> Check, with retry.

This is the only module that ties planner.py, actor.py, and checker.py
together, so the loop itself -- including the retry cap that guards
against infinite loops -- lives in exactly one place.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

from .actor import ActorError, execute_plan
from .checker import run_checks
from .logger import get_logger
from .planner import build_plan
from .recommender import load_songs

logger = get_logger()

MAX_ATTEMPTS = 3


@dataclass
class AgentRunResult:
    user_request: str
    attempts: int
    verified: bool
    formatted: List[Dict]
    log_trail: List[Dict]


def _catalog_genres_moods(catalog_path: str):
    """Best-effort lookup of the catalog's known genres/moods, for grounding the planner."""
    try:
        songs = load_songs(catalog_path)
        genres = sorted({s["genre"] for s in songs})
        moods = sorted({s["mood"] for s in songs})
        return genres, moods
    except Exception as exc:  # noqa: BLE001 - a bad catalog here is reported, not fatal at this stage
        logger.error("Could not read catalog for planner grounding (%s); using minimal defaults", exc)
        return ["pop"], ["happy"]


def run_agent(user_request: str, catalog_path: str = "data/songs.csv") -> AgentRunResult:
    """
    Runs the plan -> act -> check loop for a single user request.

    Guardrails:
    - Invalid user_request is validated up front (planner.build_plan raises
      ValueError on empty input) rather than silently producing garbage.
    - Every attempt is wrapped in try/except so a single bad attempt
      (a transient error, a malformed plan) doesn't crash the whole run --
      it's logged and counted as a failed attempt, and the loop moves on.
    - MAX_ATTEMPTS caps the retry loop so a persistently failing check
      can never spin forever; after the cap, the best available result is
      returned with 'verified=False' rather than raising.
    """
    if not isinstance(user_request, str) or not user_request.strip():
        raise ValueError("user_request must be a non-empty string")

    known_genres, known_moods = _catalog_genres_moods(catalog_path)

    log_trail = []
    feedback = None
    last_actor_result = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        logger.info("=== Attempt %d/%d for request: %r ===", attempt, MAX_ATTEMPTS, user_request)

        try:
            plan = build_plan(user_request, known_genres, known_moods, feedback=feedback)
            actor_result = execute_plan(plan, catalog_path)
            check_result = run_checks(user_request, actor_result)

            log_trail.append({
                "attempt": attempt,
                "plan_source": plan.source,
                "preferences": plan.preferences,
                "strategy": plan.strategy,
                "check_layer": check_result.layer,
                "check_passed": check_result.passed,
                "check_reason": check_result.reason,
            })

            last_actor_result = actor_result

            if check_result.passed:
                logger.info("=== Attempt %d PASSED check (%s layer) ===", attempt, check_result.layer)
                return AgentRunResult(
                    user_request=user_request,
                    attempts=attempt,
                    verified=True,
                    formatted=actor_result.formatted,
                    log_trail=log_trail,
                )

            logger.warning(
                "=== Attempt %d FAILED check (%s layer): %s ===",
                attempt, check_result.layer, check_result.reason,
            )
            feedback = check_result.suggested_fix

        except ActorError as exc:
            logger.error("Attempt %d aborted: actor error: %s", attempt, exc)
            log_trail.append({"attempt": attempt, "error": str(exc)})
            feedback = {"reason": "actor_error"}

        except Exception as exc:  # noqa: BLE001 - never let one bad attempt crash the whole run
            logger.error("Attempt %d aborted: unexpected error: %s", attempt, exc)
            log_trail.append({"attempt": attempt, "error": str(exc)})
            feedback = {"reason": "unexpected_error"}

    logger.warning(
        "All %d attempts exhausted without passing checks; returning best-effort, unverified result",
        MAX_ATTEMPTS,
    )
    return AgentRunResult(
        user_request=user_request,
        attempts=MAX_ATTEMPTS,
        verified=False,
        formatted=last_actor_result.formatted if last_actor_result else [],
        log_trail=log_trail,
    )
