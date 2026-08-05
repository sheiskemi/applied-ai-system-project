"""
Thin wrapper around the Anthropic API shared by planner.py and checker.py.

Centralizing this here means both the Planner and the Checker's semantic
layer get identical guardrails (missing key, network errors, malformed
JSON, retries) for free, instead of re-implementing error handling twice
and risking the two copies drifting apart.
"""

import json
import os
import time
from typing import Optional

from .logger import get_logger

logger = get_logger()

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # python-dotenv is a required dependency (requirements.txt), but if it's
    # somehow missing, ANTHROPIC_API_KEY can still be set directly in the
    # environment -- there's no reason to crash the whole agent over it.
    pass

DEFAULT_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5")
MAX_LLM_RETRIES = 2
RETRY_BACKOFF_SECONDS = 1.5

_client = None
_client_checked = False


def get_client():
    """
    Returns a configured Anthropic client, or None if unavailable.

    Missing SDK, missing API key, and client construction errors are all
    treated as "no LLM available" rather than raised -- callers use this to
    decide whether to fall back to deterministic planning/checking. That
    fallback is what keeps the whole system runnable for someone who
    hasn't set up an API key yet.
    """
    global _client, _client_checked

    if _client_checked:
        return _client

    _client_checked = True

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        logger.warning("ANTHROPIC_API_KEY not set; LLM features will use deterministic fallback")
        return None

    try:
        import anthropic
    except ImportError:
        logger.warning("anthropic package not installed; LLM features will use deterministic fallback")
        return None

    try:
        _client = anthropic.Anthropic(api_key=api_key)
    except Exception as exc:
        logger.error("Failed to construct Anthropic client (%s); using deterministic fallback", exc)
        _client = None

    return _client


def call_llm_json(system_prompt: str, user_prompt: str, max_tokens: int = 1024) -> Optional[dict]:
    """
    Calls the LLM and parses a JSON object from its response text.

    Returns None on any failure (no client, network/API error, or a
    response that isn't valid JSON) instead of raising -- the caller
    (planner/checker) is expected to fall back to deterministic logic
    rather than crash the whole agent run over a transient API hiccup.
    """
    client = get_client()
    if client is None:
        return None

    import anthropic

    last_error = None
    for attempt in range(1, MAX_LLM_RETRIES + 1):
        try:
            response = client.messages.create(
                model=DEFAULT_MODEL,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            text = "".join(
                block.text for block in response.content if getattr(block, "type", None) == "text"
            ).strip()

            # Models sometimes wrap JSON in ```json fences despite instructions not to.
            if text.startswith("```"):
                text = text.strip("`")
                if text.startswith("json"):
                    text = text[4:]
                text = text.strip()

            return json.loads(text)

        except (anthropic.APIConnectionError, anthropic.APIStatusError, anthropic.RateLimitError) as exc:
            last_error = exc
            logger.warning("LLM call failed (attempt %d/%d): %s", attempt, MAX_LLM_RETRIES, exc)
            if attempt < MAX_LLM_RETRIES:
                time.sleep(RETRY_BACKOFF_SECONDS * attempt)

        except json.JSONDecodeError as exc:
            last_error = exc
            logger.warning(
                "LLM response was not valid JSON (attempt %d/%d): %s", attempt, MAX_LLM_RETRIES, exc
            )
            if attempt < MAX_LLM_RETRIES:
                time.sleep(RETRY_BACKOFF_SECONDS * attempt)

        except Exception as exc:  # noqa: BLE001 - any unexpected SDK error must not crash the agent
            last_error = exc
            logger.error("Unexpected error calling LLM: %s", exc)
            break

    logger.error("LLM call ultimately failed after %d attempt(s): %s", MAX_LLM_RETRIES, last_error)
    return None
