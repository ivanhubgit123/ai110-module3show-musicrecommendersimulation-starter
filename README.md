# 🎵 Music Recommender Simulation

## Project Summary

This project is a small, content-based music recommender called **VibeFinder 1.0**. It reads a
catalog of songs from a CSV file, compares each song to a user's "taste profile," and returns a
ranked list of the best matches — along with a plain-language reason for every recommendation.

The goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

---

## How The System Works

**How real systems do it.** Big platforms like Spotify and YouTube mostly use two ideas.
*Collaborative filtering* recommends songs by looking at other users' behavior — "people who
liked what you liked also played this." *Content-based filtering* ignores other users and instead
compares the actual attributes of the items — tempo, mood, genre — to what you tend to enjoy. Real
systems blend both and add signals like likes, skips, and how long you listen before skipping.

**What my version does.** VibeFinder is purely *content-based*. It has no other users, so it can't
do collaborative filtering. It compares each song's attributes directly to a user's stated
preferences and scores the fit.

**Features each `Song` uses:** `genre`, `mood`, `energy` (0.0–1.0), `tempo_bpm`, `valence`,
`danceability`, `acousticness`, plus the advanced features added in the extensions: `popularity`
(0–100), `release_decade`, `mood_tags` (detailed tags like `nostalgic|warm`), `instrumental`, and
`language`. My scoring uses **genre, mood, energy, acousticness, release_decade, mood_tags, and
popularity**.

**What the `UserProfile` stores:** `favorite_genre`, `favorite_mood`, `target_energy`,
`likes_acoustic`, and optionally `favorite_decade` and `desired_tags`. (The functional API in
`main.py` uses the equivalent dict keys `genre`, `mood`, `energy`, `likes_acoustic`, `decade`,
`tags`.)

**How a score is computed (the Algorithm Recipe):**

| Rule | Points |
|------|--------|
| Genre matches the user's favorite genre | **+2.0** |
| Mood matches the user's favorite mood | **+1.0** |
| Energy closeness: `2.0 × (1 − |target_energy − song_energy|)` | **0.0 – 2.0** |
| Acoustic bonus (only if user likes acoustic *and* song's acousticness ≥ 0.6) | **+0.5** |
| Release-decade match (only if user gives a `decade`) | **+1.0** |
| Mood-tag overlap (only if user gives `tags`) | **+0.5 per tag** |
| Popularity nudge | **+0.5 × (popularity ÷ 100)** |

The energy rule is a *similarity* score, not a "higher is better" score — a song is rewarded for
being **close** to the target energy in either direction. Genre is weighted highest because it's
the strongest signal of taste; mood is a softer nudge. The weights themselves are swappable via
scoring **modes** (see Optional Extensions below).

**Why two rules?** A **Scoring Rule** judges *one* song and produces a number. A **Ranking Rule**
applies the scoring rule to *every* song and sorts them, so we can pick the top *k*. You need both:
scoring alone gives you numbers with no order; ranking is what turns those numbers into a
recommendation list.

**Data flow:** User prefs → score every song in the CSV (the loop) → sort by score → return top *k*.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows
   ```

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

Actual terminal output from `python -m src.main` (catalog of 18 songs, balanced scoring mode).
The CLI also prints scoring-mode and diversity-penalty demos — see Optional Extensions.

```
Loaded songs: 18

Profile: Happy Pop (default)  prefs: {'genre': 'pop', 'mood': 'happy', 'energy': 0.8}
1. Sunrise City — Neon Echo [pop/happy]  Score 5.40
   genre match (pop) +2.0; mood match (happy) +1.0; energy close to 0.80 (song 0.82) +1.96; popularity 88/100 +0.44
2. Gym Hero — Max Pulse [pop/intense]  Score 4.15
   genre match (pop) +2.0; energy close to 0.80 (song 0.93) +1.74; popularity 81/100 +0.41
3. Rooftop Lights — Indigo Parade [indie pop/happy]  Score 3.29
   mood match (happy) +1.0; energy close to 0.80 (song 0.76) +1.92; popularity 74/100 +0.37
4. Concrete Kings — Vex Dial [hip hop/aggressive]  Score 2.37
   energy close to 0.80 (song 0.84) +1.92; popularity 90/100 +0.45
5. Night Drive Loop — Neon Echo [synthwave/moody]  Score 2.24
   energy close to 0.80 (song 0.75) +1.9; popularity 68/100 +0.34

Profile: Chill Lofi  prefs: {'genre': 'lofi', 'mood': 'chill', 'energy': 0.35, 'likes_acoustic': True}
1. Library Rain — Paper Lanterns [lofi/chill]  Score 5.79
   genre match (lofi) +2.0; mood match (chill) +1.0; energy close to 0.35 (song 0.35) +2.0; acoustic pick (0.86) +0.5; popularity 59/100 +0.29
2. Midnight Coding — LoRoom [lofi/chill]  Score 5.68
   genre match (lofi) +2.0; mood match (chill) +1.0; energy close to 0.35 (song 0.42) +1.86; acoustic pick (0.71) +0.5; popularity 64/100 +0.32
3. Focus Flow — LoRoom [lofi/focused]  Score 4.70
   genre match (lofi) +2.0; energy close to 0.35 (song 0.40) +1.9; acoustic pick (0.78) +0.5; popularity 61/100 +0.3
4. Spacewalk Thoughts — Orbit Bloom [ambient/chill]  Score 3.59
   mood match (chill) +1.0; energy close to 0.35 (song 0.28) +1.86; acoustic pick (0.92) +0.5; popularity 47/100 +0.23
5. Coffee Shop Stories — Slow Stereo [jazz/relaxed]  Score 2.74
   energy close to 0.35 (song 0.37) +1.96; acoustic pick (0.89) +0.5; popularity 55/100 +0.28

Profile: Deep Intense Rock  prefs: {'genre': 'rock', 'mood': 'intense', 'energy': 0.9}
1. Storm Runner — Voltline [rock/intense]  Score 5.34
   genre match (rock) +2.0; mood match (intense) +1.0; energy close to 0.90 (song 0.91) +1.98; popularity 72/100 +0.36
2. Gym Hero — Max Pulse [pop/intense]  Score 3.35
   mood match (intense) +1.0; energy close to 0.90 (song 0.93) +1.94; popularity 81/100 +0.41
3. Concrete Kings — Vex Dial [hip hop/aggressive]  Score 2.33
   energy close to 0.90 (song 0.84) +1.88; popularity 90/100 +0.45
4. Neon Warehouse — Pulse Theory [edm/energetic]  Score 2.32
   energy close to 0.90 (song 0.95) +1.9; popularity 85/100 +0.42
5. Sunrise City — Neon Echo [pop/happy]  Score 2.28
   energy close to 0.90 (song 0.82) +1.84; popularity 88/100 +0.44

Profile: Conflicted (loud + sad)  prefs: {'genre': 'folk', 'mood': 'sad', 'energy': 0.9}
1. Broken Compass — Ash Meridian [folk/sad]  Score 4.08
   genre match (folk) +2.0; mood match (sad) +1.0; energy close to 0.90 (song 0.31) +0.82; popularity 52/100 +0.26
2. Gym Hero — Max Pulse [pop/intense]  Score 2.35
   energy close to 0.90 (song 0.93) +1.94; popularity 81/100 +0.41
3. Storm Runner — Voltline [rock/intense]  Score 2.34
   energy close to 0.90 (song 0.91) +1.98; popularity 72/100 +0.36
4. Concrete Kings — Vex Dial [hip hop/aggressive]  Score 2.33
   energy close to 0.90 (song 0.84) +1.88; popularity 90/100 +0.45
5. Neon Warehouse — Pulse Theory [edm/energetic]  Score 2.32
   energy close to 0.90 (song 0.95) +1.9; popularity 85/100 +0.42

Profile: Nostalgia Trip (tags+decade)  prefs: {'genre': 'country', 'mood': 'nostalgic', 'energy': 0.5, 'decade': 1990, 'tags': ['nostalgic', 'warm']}
1. Amber Fields — Willow Grange [country/nostalgic]  Score 7.27
   genre match (country) +2.0; mood match (nostalgic) +1.0; energy close to 0.50 (song 0.49) +1.98; decade match (1990s) +1.0; mood tags ['nostalgic', 'warm'] +1.0; popularity 58/100 +0.29
2. Velvet Hours — Cielo Rae [r&b/romantic]  Score 2.81
   energy close to 0.50 (song 0.54) +1.92; mood tags ['warm'] +0.5; popularity 77/100 +0.39
...
```

> The live CLI renders these as full `tabulate` grid tables (Challenge 4).

---

## Experiments You Tried

- **Conflicting preferences (loud + sad).** I gave the recommender a profile with `mood: sad` but
  `energy: 0.9`. Almost no real song is both very sad *and* very high energy, so the genre+mood
  match (`Broken Compass`, +3.0) beats every high-energy song even though its energy is far off the
  target. This shows the categorical weights dominate the numeric similarity score.
- **Genre weight sensitivity.** Because a genre match alone is worth +2.0 and energy closeness maxes
  at +2.0, a same-genre song almost always outranks a different-genre song at the same energy. If I
  dropped the genre weight to 0.5, energy and mood would start to drive the rankings instead.

---

## Optional Extensions

All four optional challenges are implemented (agentic workflow notes live in `ai_interactions.md`):

1. **Advanced song features** — added `popularity`, `release_decade`, `mood_tags`, `instrumental`,
   and `language` to `data/songs.csv` and to the scoring logic (decade match, tag overlap,
   popularity nudge).
2. **Multiple scoring modes (Strategy pattern)** — `ScoringStrategy` bundles the weights, and
   `STRATEGIES` exposes `balanced`, `genre-first`, `mood-first`, and `energy-focused`. Pass one via
   `recommend_songs(..., strategy=STRATEGIES["mood-first"])`. Same prefs, very different rankings.
3. **Diversity penalty** — `recommend_songs(..., diversity_penalty=1.5)` greedily subtracts points
   for each already-picked song with the same artist or genre, so the top list isn't dominated by
   one artist. In the demo it drops a repeated-artist track and promotes a different-genre song.
4. **Formatted table** — `main.py` prints results with `tabulate` (grid format) and falls back to
   plain text if `tabulate` isn't installed.

---

## Limitations and Risks

- Tiny catalog (18 songs), so variety in the top 5 is limited.
- Pure content-based: no collaborative filtering, no "users like you also enjoyed."
- Only exact genre/mood string matches count — "indie pop" does not partially match "pop."
- It doesn't understand lyrics, language, or artist similarity.
- Categorical weights (genre + mood) can dominate the numeric energy fit.

More detail lives in the model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Building this made the core idea of a recommender concrete: a recommendation is just a *scoring
rule* applied to every item and then sorted. There's no magic — the "taste" of the system lives
entirely in the weights I chose, and changing a single number (like the genre weight) visibly
reshapes the whole list.

It also made bias easy to see. Because my catalog leans toward pop and lofi, and because genre is
the heaviest weight, users whose favorite genre is well-represented get rich, varied results, while
users in sparse genres fall back to whatever merely matches on energy. In a real system trained on
millions of users, that same "give more to the already-popular" dynamic is exactly how filter
bubbles and popularity bias form.
