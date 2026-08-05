"""
Command line runner for the Music Recommender Simulation.

Runs each request through the agentic Plan -> Act -> Check loop
(src/agent.py) instead of calling the recommender directly, so every run
produces a logged plan, a logged action trail, and a logged check verdict
-- including a retry if the check fails.

Usage:
    python -m src.main                       # runs the built-in demo requests
    python -m src.main "some free-text ask"   # runs a single custom request
"""

import sys

from .agent import run_agent

# Windows consoles often default stdout to cp1252, which can't encode the
# emoji used in the formatted output below. print() would then raise
# UnicodeEncodeError -- a subclass of ValueError -- which looks identical
# to the "invalid request" guardrail in main() and would misreport a
# successful run as a rejected one. Forcing utf-8 avoids that ambiguity.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

# The built-in demo intentionally includes one edge case (a happy, high-
# energy request for a genre the catalog only has a slow/melancholy example
# of) that the deterministic pre-check is expected to reject on the first
# attempt, so a full plan -> act -> check -> retry -> act -> check cycle is
# visible in the logs even with no ANTHROPIC_API_KEY configured.
DEMO_REQUESTS = [
    "I want upbeat happy pop songs for a workout",
    "Something chill and relaxed for studying, lofi vibes",
    "Deep intense rock to get pumped up",
    "I'm a happy classical music fan feeling energetic",
]


def _print_result(result) -> None:
    print("\n" + "=" * 60)
    print(f"Request: {result.user_request!r}")
    print(f"Verified: {result.verified} (after {result.attempts} attempt(s))")
    print("=" * 60)

    if not result.formatted:
        print("No recommendations could be produced.")
        return

    for song in result.formatted:
        print(f"🎵 {song['title']} by {song['artist']}")
        print(f"Genre: {song['genre']} | Mood: {song['mood']}")
        print(f"Score: {song['score']:.2f}")
        print(f"Why: {song['explanation']}")
        print("-" * 60)


def main() -> None:
    custom_request = " ".join(sys.argv[1:]).strip()
    requests_to_run = [custom_request] if custom_request else DEMO_REQUESTS

    for request in requests_to_run:
        try:
            result = run_agent(request)
            _print_result(result)
        except ValueError as exc:
            # Guardrail: invalid input (e.g. blank request) is reported
            # clearly instead of letting a traceback end the whole run.
            print(f"\nSkipping invalid request {request!r}: {exc}")


if __name__ == "__main__":
    main()