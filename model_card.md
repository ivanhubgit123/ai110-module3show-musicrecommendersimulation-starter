# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Intended Use

VibeFinder recommends songs from a small fixed catalog by matching each song's attributes to a
user's stated taste profile (favorite genre, favorite mood, target energy, and whether they like
acoustic music). It returns a ranked top-5 list with a plain-language reason for each pick.

- **What it generates:** a ranked, explained shortlist of songs for one user profile.
- **Assumptions:** the user can name a favorite genre, a favorite mood, and a rough energy level,
  and that those stated preferences reflect what they actually want to hear.
- **Who it's for:** classroom exploration and learning how content-based recommenders work. It is
  **not** a production system for real listeners.

---

## 3. How the Model Works

Imagine a scorecard. For every song, VibeFinder starts at zero and adds points:

- **+2 points** if the song's genre is your favorite genre.
- **+1 point** if the song's mood is your favorite mood.
- **Up to +2 points** for energy, based on how *close* the song's energy is to what you asked for.
  A perfect match gets the full 2; the farther off it is, the fewer points — in either direction.
- **+0.5 bonus** if you said you like acoustic music and the song is genuinely acoustic.

After every song has a score, VibeFinder sorts them from highest to lowest and shows you the top 5,
listing exactly which rules earned the points. Change to the starter logic: I added the **energy
closeness** score (rewarding nearness, not loudness) and the **acoustic bonus**, and I made the
system explain each recommendation in words. In the optional extensions I also added scoring for
**release decade**, **detailed mood tags**, and **popularity**, made the weights swappable via
scoring "modes" (genre-first, mood-first, energy-focused), and added a diversity penalty so the
top list isn't all one artist.

---

## 4. Data

- **Size:** 18 songs (10 starter + 8 I added).
- **Genres represented:** pop, indie pop, lofi, rock, metal, edm, hip hop, r&b, jazz, folk,
  country, classical, reggae, ambient, synthwave.
- **Moods represented:** happy, chill, intense, relaxed, moody, focused, energetic, sad,
  aggressive, romantic, nostalgic.
- **Features per song:** genre, mood, energy, tempo_bpm, valence, danceability, acousticness, and
  the advanced features popularity (0–100), release_decade, mood_tags, instrumental, and language.
- **Changes I made:** added 8 songs covering genres/moods missing from the starter (edm, hip hop,
  metal, r&b, folk, country, classical, reggae; moods like sad, romantic, aggressive, nostalgic),
  and added 5 advanced feature columns to every song.
- **What's missing:** the catalog still leans toward pop/lofi/electronic. There is no world/latin
  representation, no lyrics content, and only a single non-English tag — the `language` column is
  almost entirely `english`/`instrumental`, so it can't really support language-based taste.

---

## 5. Strengths

- Works well for users whose favorite genre is in the catalog (pop, lofi, rock) — those profiles
  get a clear, on-theme top pick with a high score.
- The energy-closeness rule correctly pulls chill profiles toward low-energy songs and gym/rock
  profiles toward high-energy songs.
- Every recommendation is explained, so it's easy to see *why* a song ranked where it did.
- Matched my intuition: for "Chill Lofi," the top two are both actual lofi/chill tracks, and the
  quietest, most acoustic songs rise to the top.

---

## 6. Limitations and Bias

- **Genre dominates.** A genre match is worth +2.0 — as much as a perfect energy match — so a
  same-genre song almost always beats a different-genre song even when the second one fits the
  user's energy and mood better. This is a built-in **filter bubble**: the system keeps handing you
  more of your favorite genre and rarely surprises you with something adjacent.
- **Popularity/representation bias.** Genres with more songs in the catalog (pop, lofi) give those
  users varied results, while a user in a sparse genre (e.g., reggae) mostly gets songs that only
  match on energy. The dataset's imbalance becomes the recommender's blind spot.
- **Exact-match only.** "indie pop" does not partially credit a "pop" fan, even though they're close.
- **Popularity bias (from the extensions).** The popularity nudge means a well-known song gets a
  small edge on every profile — a mild version of the "rich get richer" dynamic real platforms show.
- **Ignores some features.** tempo_bpm, valence, danceability, and language are loaded but never scored.
- **Conflicting profiles expose the seams.** For a "loud + sad" user, the +3.0 from genre+mood
  overwhelms a nearly-zero energy score, so a quiet sad song wins despite the user asking for high
  energy — the system can't tell the user their request is self-contradictory.

---

## 7. Evaluation

I tested four profiles: **Happy Pop** (default), **Chill Lofi**, **Deep Intense Rock**, and an
adversarial **Conflicted (loud + sad)** profile.

- **What I looked for:** whether the #1 pick actually matched the profile, and whether the energy
  rule moved the list in the expected direction.
- **Profile comparisons:**
  - *Happy Pop vs. Chill Lofi:* the Pop profile surfaces bright, high-energy pop
    (Sunrise City, 5.40), while the Lofi profile shifts entirely to low-energy, acoustic tracks
    (Library Rain, 5.79). This confirms the energy and acoustic rules do real work — the two lists
    share no songs.
  - *Deep Intense Rock vs. Conflicted (loud + sad):* both ask for energy ~0.9, but Rock gets a clean
    rock/intense #1 (Storm Runner, 5.34) whereas the Conflicted profile's #1 is a *quiet* folk/sad
    song (Broken Compass, 4.08) that wins on genre+mood despite failing the energy request. Same
    energy target, very different results — because the categorical weights, not energy, decide it.
- **What surprised me:** `Gym Hero` (pop/intense) shows up in three of the four lists. It's a high-
  energy pop song, so it scores well on energy for almost any energetic profile *and* gets the pop
  genre bonus — a small preview of how one "generically appealing" item can dominate rankings.

**Explaining it to a non-programmer:** "Gym Hero keeps popping up for the Happy Pop crowd because
it's both pop (which earns the big genre bonus) and very high energy (which is close to what those
users asked for). It scores points on two rules at once, so it beats songs that only match one."

---

## 8. Future Work

- **Rebalance the weights** or normalize them so genre can't single-handedly decide the ranking.
- **Use the still-unused features** (valence, danceability, tempo) so "vibe" is richer.
- **Partial genre matching** so "indie pop" gives partial credit to a "pop" fan.
- **Grow and balance the catalog** so under-represented genres get fair treatment.
- *(Already prototyped in the extensions: swappable scoring modes and a diversity penalty — a next
  step would be exposing these as CLI flags so a user can pick their own mode at runtime.)*

---

## 9. Personal Reflection

The biggest thing I learned is that a recommendation is not magic — it's just a scoring rule applied
to every item and then sorted, and the system's whole "personality" lives in a handful of weights I
picked by hand. My biggest "aha" moment was the conflicting profile: watching a quiet sad song win
for a user who asked for loud music made it obvious how much power the genre and mood weights hold.

AI tools helped me move fast on the boilerplate (CSV parsing, sorting the Pythonic way) and on
brainstorming edge-case profiles to test, but I had to double-check the scoring math myself —
especially that the energy rule rewarded *closeness* rather than just high values. What surprised me
most is how convincing such a simple algorithm feels: with just four rules and a reason string, the
output genuinely reads like a thoughtful recommendation. It made me realize that real apps like
Spotify are the same idea scaled up massively — and that the same simplicity is exactly where bias
and filter bubbles quietly creep in.
