# System Explanation & Trustworthiness

## 1. What the system does

The Music Recommender is a content-based recommendation system that takes a
free-text request (e.g. *"something chill and relaxed for studying"*) and
returns ranked song recommendations from a small catalog, along with a
plain-language explanation of why each song was chosen.

The underlying recommendation logic (`src/recommender.py`) scores songs by
comparing genre, mood, and energy against the user's stated preferences.
This scoring engine is unchanged from the original project.

What's new is the layer wrapped around it: instead of calling the
recommender directly, every request now goes through an **agentic
Plan → Act → Check workflow** that interprets the request, executes it in
discrete steps, verifies the result, and retries with a revised approach
if the result doesn't hold up.

## 2. How the system reasons

The workflow has four stages, each in its own module:

- **Plan** (`src/planner.py`) — Converts the free-text request into
  structured preferences (genre/mood/energy) and a step-by-step plan.
  Uses an LLM call when an API key is available; falls back to
  deterministic keyword parsing otherwise.
- **Act** (`src/actor.py`) — Executes the plan as four independent,
  logged steps: `validate_input → load_catalog → score_and_rank →
  format_output`.
- **Check** (`src/checker.py`) — Verifies the output. A deterministic
  layer always runs first (catches empty results, out-of-range scores,
  and genre-only matches with a poor mood/energy fit). An optional LLM
  semantic check runs on top of that when available.
- **Orchestrate** (`src/agent.py`) — Runs the loop above. If the Checker
  fails a result, the Agent re-plans (e.g. drops a genre constraint that
  produced a bad match) and retries, capped at `MAX_ATTEMPTS = 3`.

This isn't a check that just prints a warning next to the original
output — a failed check changes what the Planner does on the next
attempt, which changes what the Actor scores, which changes the final
result the user sees. The sample log below shows this concretely: on
attempt 1, `require_genre_match` is `True` and the check fails; on
attempt 2, the Planner sets it to `False` in direct response to the
Checker's failure reason, and the check passes on different output.

```text
[PLAN] (deterministic_fallback) preferences={'genre': 'classical', ...}
       strategy={'require_genre_match': True, 'k': 5}
[CHECK] (deterministic) passed=False reason=top score 2.35 clears the
        threshold on genre match alone, but mood and energy are a poor fit
=== Attempt 1 FAILED check ===

Deterministic planner relaxing genre requirement per retry feedback
[PLAN] (deterministic_fallback) strategy={'require_genre_match': False, 'k': 5}
[CHECK] (deterministic) passed=True reason=structural checks passed
=== Attempt 2 PASSED check ===
```

## 3. Why it's trustworthy

Trustworthiness here comes from two things: the system has guardrails,
and those guardrails were actually verified to work — not assumed to
work. While integrating and testing the agentic layer, I found and fixed
four real problems, three of which were guardrail or reliability bugs
rather than feature bugs:

1. **The retry demo didn't actually trigger a retry at first.** A
   genre-only match was scoring high enough to pass the Checker even
   with a bad mood/energy fit, so the "check catches a bad output"
   behavior wasn't actually happening — it just looked like it should
   on paper. I added a specific deterministic check for a genre-match/
   mood-mismatch case to close this gap.

2. **The retry loop could have failed silently forever.** After the
   Planner relaxed the genre requirement, the Actor was still passing
   the *original* genre into the scorer — so every retry attempt
   produced the identical result and would have failed identically up
   to `MAX_ATTEMPTS`, never actually benefiting from the re-plan. This
   is the kind of bug that's dangerous specifically because the system
   *looks* like it's retrying (the log shows "Attempt 2/3") while
   silently doing nothing different. Fixed by having the Actor drop the
   genre from scoring when the Planner marks it relaxed.

3. **A real crash was being misreported as a normal validation
   failure.** On Windows, printing the 🎵 emoji to a `cp1252` console
   raised a `UnicodeEncodeError`, which is a subclass of `ValueError` —
   the same exception type used for invalid-input guardrails. As a
   result, every successful run was being logged as "invalid request,"
   which is a worse failure mode than an obvious crash: it's a
   guardrail actively hiding a bug instead of catching one. Fixed by
   forcing UTF-8 stdout at startup.

4. **`.env` files were silently ignored.** `python-dotenv` was listed
   as a dependency but `load_dotenv()` was never called, so setting an
   API key in `.env` had no effect and the system would silently run in
   fallback mode. Fixed by calling `load_dotenv()` in `llm_client.py`
   and adding `.env.example` to make the expected setup explicit.

None of these were found by assuming the guardrails worked — they were
found by running the system, reading the actual logs, and checking that
the *reported* behavior matched the *real* behavior. That process is the
core trustworthiness claim of this project: not "the system has
guardrails," but "the guardrails were tested against real failure modes
and three separate bugs that would have undermined them were caught and
fixed before submission."

## 4. Known limitations

- The recommendation engine itself only scores on genre, mood, and
  energy — it doesn't use tempo, lyrics, listening history, or
  feedback, and the catalog is small (18 songs), so recommendations can
  repeat across different requests.
- The LLM-backed Planner and semantic Checker are optional — without an
  `ANTHROPIC_API_KEY`, the system runs entirely on deterministic
  fallback logic. This is a deliberate design choice for reliability,
  but it means the "agentic reasoning" is weaker in that mode: the
  Planner's keyword parsing is simpler than what an LLM could infer
  from a nuanced request.
- `MAX_ATTEMPTS = 3` is a fixed cap chosen for this project; it isn't
  tuned against a larger, more varied set of edge cases beyond the one
  demonstrated here.