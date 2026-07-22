"""Command line runner for the Music Recommender Simulation.

Run from the project root with:  python -m src.main

Demonstrates the core recommender plus three optional extensions:
- multiple scoring modes (Strategy pattern)
- a diversity penalty on repeated artists/genres
- a formatted results table
"""

from src.recommender import load_songs, recommend_songs, STRATEGIES

# tabulate is optional; fall back to plain rows if it isn't installed (Challenge 4).
try:
    from tabulate import tabulate
    HAVE_TABULATE = True
except ImportError:
    HAVE_TABULATE = False

# Diverse taste profiles used to stress-test the recommender (Phase 4).
PROFILES = {
    "Happy Pop (default)": {"genre": "pop", "mood": "happy", "energy": 0.8},
    "Chill Lofi": {"genre": "lofi", "mood": "chill", "energy": 0.35, "likes_acoustic": True},
    "Deep Intense Rock": {"genre": "rock", "mood": "intense", "energy": 0.9},
    # Adversarial: conflicting energy vs mood (loud but sad).
    "Conflicted (loud + sad)": {"genre": "folk", "mood": "sad", "energy": 0.9},
    # Uses the advanced features: mood tags + release decade.
    "Nostalgia Trip (tags+decade)": {
        "genre": "country", "mood": "nostalgic", "energy": 0.5,
        "decade": 1990, "tags": ["nostalgic", "warm"],
    },
}


def render_table(title: str, rows: list) -> None:
    """Print recommendations as a formatted table, with an ASCII fallback."""
    print(f"\n{'=' * 70}\n{title}\n{'-' * 70}")
    headers = ["#", "Title", "Artist", "Genre/Mood", "Score", "Reasons"]
    if HAVE_TABULATE:
        print(tabulate(rows, headers=headers, tablefmt="grid", maxcolwidths=[3, 20, 14, 16, 6, 42]))
    else:
        for r in rows:
            print(f"{r[0]}. {r[1]} — {r[2]} [{r[3]}]  score={r[4]}")
            print(f"     {r[5]}")


def build_rows(user_prefs: dict, songs: list, **kwargs) -> list:
    """Turn recommendations into table rows."""
    recs = recommend_songs(user_prefs, songs, k=5, **kwargs)
    rows = []
    for rank, (song, score, explanation) in enumerate(recs, start=1):
        rows.append([rank, song["title"], song["artist"],
                     f"{song['genre']}/{song['mood']}", f"{score:.2f}", explanation])
    return rows


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    # 1) Core: every profile with the default balanced strategy.
    print("\n########## CORE: balanced scoring ##########")
    for title, prefs in PROFILES.items():
        render_table(f"Profile: {title}\n  prefs: {prefs}", build_rows(prefs, songs))

    # 2) Extension: same profile, different scoring modes (Strategy pattern).
    print("\n\n########## SCORING MODES (Strategy pattern) ##########")
    demo = {"genre": "pop", "mood": "chill", "energy": 0.4}
    for mode in ("genre-first", "mood-first", "energy-focused"):
        render_table(f"Mode: {mode}  |  prefs: {demo}",
                     build_rows(demo, songs, strategy=STRATEGIES[mode]))

    # 3) Extension: diversity penalty vs. none (Neon Echo appears twice in the catalog).
    print("\n\n########## DIVERSITY PENALTY ##########")
    div_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    render_table("No penalty", build_rows(div_prefs, songs, diversity_penalty=0.0))
    render_table("Penalty = 1.5 (repeated artist/genre pushed down)",
                 build_rows(div_prefs, songs, diversity_penalty=1.5))


if __name__ == "__main__":
    main()
