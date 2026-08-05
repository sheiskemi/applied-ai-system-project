"""
Demonstrates the full Plan -> Act -> Check (-> retry) cycle.

The LLM layer is monkeypatched to "unavailable" in every test here so the
suite is 100% reproducible without an ANTHROPIC_API_KEY or network access
-- these tests exercise the deterministic planner fallback and the
deterministic pre-check layer, which is exactly the code path the project
guarantees works out of the box. With a real API key set, `python -m
src.main` additionally exercises the LLM-backed planner/checker layers.
"""

import pytest

import src.checker as checker
import src.planner as planner
from src.actor import ActorError, load_catalog, validate_input
from src.agent import run_agent


@pytest.fixture(autouse=True)
def no_llm(monkeypatch):
    """Forces every test onto the deterministic fallback path, for reproducibility."""
    monkeypatch.setattr(planner, "call_llm_json", lambda *a, **k: None)
    monkeypatch.setattr(checker, "call_llm_json", lambda *a, **k: None)


def test_normal_request_passes_on_first_attempt():
    result = run_agent("I want upbeat happy pop songs for a workout")

    assert result.verified is True
    assert result.attempts == 1
    assert len(result.formatted) > 0
    assert result.log_trail[0]["check_passed"] is True


def test_edge_case_fails_first_attempt_then_retries_and_passes():
    """
    'Happy classical, high energy' has no strong match in the catalog under a
    strict genre filter (the one classical track is slow/melancholy) -- this
    is the case that should make the deterministic checker reject attempt 1
    and force the planner to relax its strategy on attempt 2.
    """
    result = run_agent("I'm a happy classical music fan feeling energetic")

    assert result.attempts >= 2
    assert result.log_trail[0]["check_passed"] is False
    assert result.log_trail[0]["check_reason"].startswith("top score")
    assert result.log_trail[-1]["check_passed"] is True
    assert result.verified is True

    # The retry should have relaxed the strict genre requirement.
    assert result.log_trail[0]["strategy"]["require_genre_match"] is True
    assert result.log_trail[-1]["strategy"]["require_genre_match"] is False


def test_blank_request_raises_value_error():
    with pytest.raises(ValueError):
        run_agent("   ")


def test_validate_input_rejects_out_of_range_energy():
    with pytest.raises(ActorError):
        validate_input({"genre": "pop", "mood": "happy", "energy": 5.0})


def test_validate_input_rejects_missing_keys():
    with pytest.raises(ActorError):
        validate_input({"genre": "pop"})


def test_load_catalog_rejects_missing_file():
    with pytest.raises(ActorError):
        load_catalog("data/does_not_exist.csv")
