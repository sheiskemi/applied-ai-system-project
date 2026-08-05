# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I asked Claude Code to first explore this project (the Music Recommender Simulation) and summarize what it does, its file structure, and how it's run — then extend it into a full applied AI system by adding an agentic workflow: the system should PLAN a sequence of steps, ACT on that plan, and CHECK/verify its own output, correcting itself if the check fails, specifically wrapped around this project's existing recommendation logic rather than a generic bolted-on agent.

**Prompts used:**

The key prompt (condensed to its requirements) was:

> Extend it with an agentic workflow... PLAN a sequence of steps, ACT on that plan, and CHECK/verify its own output, correcting itself if the check fails. Design this specifically around what the existing project already does.
>
> 1. Plan step: Given the task/input this project handles, the AI should break it into a concrete sequence of sub-steps before doing anything. Log this plan.
> 2. Act step: Execute the plan step by step. Each action should be a discrete, loggable function (not one giant LLM call that does everything).
> 3. Check step: After acting, verify the output against a defined success criterion relevant to this project... If the check fails, the system should retry or revise — not silently continue.
> 4. Logging: Every plan, action, and check result should be logged... with timestamps.
> 5. Guardrails: Handle predictable failure modes gracefully — invalid input, API/network errors, empty/bad results, infinite retry loops (cap at N attempts). No unhandled exceptions crashing the whole run.
>
> Keep the agentic loop as a clearly separated module (e.g. planner.py, actor.py, checker.py)... Must be runnable end-to-end by someone else following a README... Add a small test script... including at least one case where the check step catches a bad output and triggers a retry/fix.

I also explicitly chose (when Claude Code asked) to make the Planner/Checker LLM-backed via the Anthropic API rather than purely rule-based, which is why `src/llm_client.py` and the deterministic-fallback design exist.

**What did the agent generate or change?**

`src/planner.py`, `src/actor.py`, `src/checker.py`, `src/agent.py`, `src/llm_client.py`, `tests/test_agent.py`, `.env.example`, plus updates to `src/main.py` (routes demo/CLI requests through the agent), `requirements.txt` (added `anthropic`, `python-dotenv`), `README.md` (Agentic Workflow section, Design Decisions, Testing Summary, sample logs, System Architecture diagram embed), `diagrams/architecture.mmd`, and `TRUSTWORTHINESS.md`.

**What did you verify or fix manually?**

I ran the full test suite and the agent end-to-end myself rather than trusting that the generated code worked as documented, and found four real bugs this way (all detailed in [TRUSTWORTHINESS.md](TRUSTWORTHINESS.md)):

1. The retry demo didn't actually trigger a retry — a genre-only match scored high enough to pass the Checker even with a bad mood/energy fit, so the "check catches bad output" behavior wasn't actually exercised.
2. The retry loop could have failed silently forever — after the Planner relaxed the genre requirement, the Actor still passed the original genre into the scorer, so every retry attempt produced an identical result up to `MAX_ATTEMPTS`.
3. A real crash was being misreported as a normal validation failure — on Windows, printing the 🎵 emoji raised `UnicodeEncodeError`, a subclass of `ValueError`, which was caught by the same guardrail used for invalid input, so every successful run was logged as "invalid request."
4. `.env` files were silently ignored — `python-dotenv` was listed as a dependency but `load_dotenv()` was never called, so an API key set in `.env` had no effect.

---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

**Which design pattern did you use?**

<!-- e.g., Strategy, Factory, Observer, etc. -->

**How did AI help you brainstorm or implement it?**

<!-- Describe the conversation or suggestions that led to your decision -->

**How does the pattern appear in your final code?**

<!-- Point to the relevant class or method -->
