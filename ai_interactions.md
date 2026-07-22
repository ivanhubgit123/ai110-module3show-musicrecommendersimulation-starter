# AI Interactions Log

> Documents the AI-assisted work on the optional stretch features.

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent to make multi-step changes autonomously.

**What task did you give the agent?**

Complete the full assignment and then implement all four optional extensions: add advanced song
features, add multiple scoring modes, add a diversity/fairness penalty, and produce a formatted
results table.

**Prompts used:**

- "Do everything the project instructions say to do."
- (Earlier) "Full build — implement all the code, expand the dataset, wire up main.py with multiple
  test profiles, run everything, and fill in the docs with real output."

**What did the agent generate or change?**

- `data/songs.csv` — expanded from 10 → 18 songs, then added 5 advanced feature columns
  (`popularity`, `release_decade`, `mood_tags`, `instrumental`, `language`).
- `src/recommender.py` — implemented `load_songs`, `score_song`, `recommend_songs`, and the
  `Recommender` class; added a `ScoringStrategy` (Strategy pattern), scoring for the new features,
  and a greedy `_apply_diversity` penalty.
- `src/main.py` — five stress-test profiles, a `tabulate` results table with plain-text fallback,
  and demo sections for the scoring modes and the diversity penalty.
- `requirements.txt` — added `tabulate`.
- `README.md` and `model_card.md` — filled in with the algorithm recipe, real terminal output,
  evaluation, biases, and reflection.
- Ran `pytest` (2 passed) and `python -m src.main` to verify output.

**What did you verify or fix manually?**

- Confirmed the `Song`/`UserProfile` dataclasses kept the original fields first with new fields
  given defaults, so the starter tests (which construct `Song` with the original 9 args) still pass.
- Checked the energy math rewards *closeness* (`1 − |Δ|`), not just high energy.
- Verified the diversity penalty actually changed the ranking (a repeated-artist track dropped out
  of the top 5 and a different-genre song moved up).

---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

**Which design pattern did you use?**

The **Strategy pattern** — each scoring "mode" is an interchangeable bundle of weights.

**How did AI help you brainstorm or implement it?**

I wanted `main.py` to switch between ranking strategies (genre-first, mood-first, energy-focused)
without duplicating the scoring loop. The AI suggested representing each mode as a small immutable
config object of weights and injecting it into the one shared scoring function, rather than writing
a separate function per mode or a tangle of `if mode == ...` branches. That keeps the scoring logic
in exactly one place and makes adding a new mode a one-line change.

**How does the pattern appear in your final code?**

- `ScoringStrategy` (a `@dataclass` of weights) in `src/recommender.py` is the strategy object.
- `STRATEGIES` is a registry of named strategies (`balanced`, `genre-first`, `mood-first`,
  `energy-focused`).
- `_score(...)`, `score_song(...)`, `recommend_songs(...)`, and `Recommender` all accept a
  `strategy` argument, defaulting to `DEFAULT_STRATEGY`. Callers swap behavior by passing a
  different strategy — e.g. `recommend_songs(prefs, songs, strategy=STRATEGIES["mood-first"])`.
