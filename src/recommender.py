"""Core recommender logic: load songs, score them against a taste profile, and rank.

Supports pluggable scoring modes (Strategy pattern) and an optional diversity penalty.
"""

import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field

ACOUSTIC_THRESHOLD = 0.6


@dataclass
class ScoringStrategy:
    """A named bundle of weights (the Strategy pattern) that defines one scoring 'mode'."""
    name: str
    genre: float = 2.0
    mood: float = 1.0
    energy: float = 2.0
    acoustic: float = 0.5
    decade: float = 1.0
    tag: float = 0.5      # per overlapping mood tag
    popularity: float = 0.5


# Selectable scoring modes (Challenge 2).
STRATEGIES: Dict[str, ScoringStrategy] = {
    "balanced": ScoringStrategy("balanced"),
    "genre-first": ScoringStrategy("genre-first", genre=3.0, mood=0.5, energy=1.0),
    "mood-first": ScoringStrategy("mood-first", genre=1.0, mood=3.0, energy=1.0, tag=1.0),
    "energy-focused": ScoringStrategy("energy-focused", genre=1.0, mood=0.5, energy=4.0),
}
DEFAULT_STRATEGY = STRATEGIES["balanced"]


@dataclass
class Song:
    """Represents a song and its attributes (advanced features default so older data still loads)."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    popularity: int = 0
    release_decade: int = 0
    mood_tags: List[str] = field(default_factory=list)
    instrumental: bool = False
    language: str = "english"


@dataclass
class UserProfile:
    """Represents a user's taste preferences (advanced prefs are optional)."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    favorite_decade: Optional[int] = None
    desired_tags: List[str] = field(default_factory=list)


def _score(song: Dict, prefs: Dict, strategy: ScoringStrategy) -> Tuple[float, List[str]]:
    """Score one normalized song view against a normalized prefs view using a strategy."""
    score = 0.0
    reasons: List[str] = []

    genre, mood, energy = song.get("genre"), song.get("mood"), song.get("energy")
    pref_genre, pref_mood = prefs.get("genre"), prefs.get("mood")
    target_energy = prefs.get("energy")

    if pref_genre and genre == pref_genre:
        score += strategy.genre
        reasons.append(f"genre match ({genre}) +{strategy.genre}")

    if pref_mood and mood == pref_mood:
        score += strategy.mood
        reasons.append(f"mood match ({mood}) +{strategy.mood}")

    if target_energy is not None and energy is not None:
        closeness = 1.0 - abs(target_energy - energy)   # 1.0 = identical, lower = further apart
        pts = round(strategy.energy * closeness, 2)
        score += pts
        reasons.append(f"energy close to {target_energy:.2f} (song {energy:.2f}) +{pts}")

    if prefs.get("likes_acoustic") and (song.get("acousticness") or 0) >= ACOUSTIC_THRESHOLD:
        score += strategy.acoustic
        reasons.append(f"acoustic pick (acousticness {song['acousticness']:.2f}) +{strategy.acoustic}")

    # --- Advanced features (Challenge 1) ---
    if prefs.get("decade") and song.get("decade") and prefs["decade"] == song["decade"]:
        score += strategy.decade
        reasons.append(f"decade match ({song['decade']}s) +{strategy.decade}")

    wanted_tags = set(prefs.get("tags") or [])
    song_tags = set(song.get("tags") or [])
    overlap = wanted_tags & song_tags
    if overlap:
        pts = round(strategy.tag * len(overlap), 2)
        score += pts
        reasons.append(f"mood tags {sorted(overlap)} +{pts}")

    popularity = song.get("popularity")
    if popularity:
        pts = round(strategy.popularity * (popularity / 100.0), 2)
        score += pts
        reasons.append(f"popularity {popularity}/100 +{pts}")

    return round(score, 2), reasons


def _apply_diversity(ranked: List[Tuple], k: int, penalty: float,
                     get_song) -> List[Tuple]:
    """Greedily pick k items, subtracting `penalty` for each already-picked same artist/genre.

    Challenge 3: prevents the top list from being dominated by one artist or genre.
    `get_song` extracts the song mapping/object from a ranked tuple.
    """
    if penalty <= 0:
        return ranked[:k]

    pool = list(ranked)
    selected: List[Tuple] = []
    seen_artists: Dict[str, int] = {}
    seen_genres: Dict[str, int] = {}

    def attr(song, key):
        return song[key] if isinstance(song, dict) else getattr(song, key)

    while pool and len(selected) < k:
        best_idx, best_adj = 0, float("-inf")
        for i, item in enumerate(pool):
            song = get_song(item)
            adj = item[1]  # base score is always element 1 of the tuple
            adj -= penalty * seen_artists.get(attr(song, "artist"), 0)
            adj -= penalty * seen_genres.get(attr(song, "genre"), 0)
            if adj > best_adj:
                best_idx, best_adj = i, adj
        chosen = pool.pop(best_idx)
        song = get_song(chosen)
        seen_artists[attr(song, "artist")] = seen_artists.get(attr(song, "artist"), 0) + 1
        seen_genres[attr(song, "genre")] = seen_genres.get(attr(song, "genre"), 0) + 1
        selected.append(chosen)
    return selected


class Recommender:
    """OOP recommender that ranks Song objects for a UserProfile."""

    def __init__(self, songs: List[Song], strategy: ScoringStrategy = DEFAULT_STRATEGY):
        self.songs = songs
        self.strategy = strategy

    def _score_song(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        """Score a single Song object against a UserProfile."""
        song_view = {
            "genre": song.genre, "mood": song.mood, "energy": song.energy,
            "acousticness": song.acousticness, "decade": song.release_decade,
            "tags": song.mood_tags, "popularity": song.popularity,
        }
        prefs_view = {
            "genre": user.favorite_genre, "mood": user.favorite_mood,
            "energy": user.target_energy, "likes_acoustic": user.likes_acoustic,
            "decade": user.favorite_decade, "tags": user.desired_tags,
        }
        return _score(song_view, prefs_view, self.strategy)

    def recommend(self, user: UserProfile, k: int = 5, diversity_penalty: float = 0.0) -> List[Song]:
        """Return the top-k Songs ranked highest-to-lowest by score."""
        scored = [(s, self._score_song(user, s)[0]) for s in self.songs]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        picked = _apply_diversity(scored, k, diversity_penalty, get_song=lambda t: t[0])
        return [song for song, _ in picked]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable string explaining why a song was recommended."""
        score, reasons = self._score_song(user, song)
        if not reasons:
            return f"No strong matches (score {score})."
        return f"Score {score}: " + "; ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV, converting numeric/list/bool columns to usable Python types."""
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["id"] = int(row["id"])
            row["tempo_bpm"] = int(row["tempo_bpm"])
            for key in ("energy", "valence", "danceability", "acousticness"):
                row[key] = float(row[key])
            # Advanced feature columns (present only in the expanded dataset).
            if "popularity" in row:
                row["popularity"] = int(row["popularity"])
            if "release_decade" in row:
                row["release_decade"] = int(row["release_decade"])
            if "mood_tags" in row:
                row["mood_tags"] = [t for t in row["mood_tags"].split("|") if t]
            if "instrumental" in row:
                row["instrumental"] = str(row["instrumental"]).strip().lower() == "true"
            songs.append(row)
    return songs


def score_song(user_prefs: Dict, song: Dict,
               strategy: ScoringStrategy = DEFAULT_STRATEGY) -> Tuple[float, List[str]]:
    """Score a single song dict against a user_prefs dict; returns (score, reasons)."""
    song_view = {
        "genre": song.get("genre"), "mood": song.get("mood"), "energy": song.get("energy"),
        "acousticness": song.get("acousticness"), "decade": song.get("release_decade"),
        "tags": song.get("mood_tags"), "popularity": song.get("popularity"),
    }
    prefs_view = {
        "genre": user_prefs.get("genre"), "mood": user_prefs.get("mood"),
        "energy": user_prefs.get("energy"), "likes_acoustic": user_prefs.get("likes_acoustic"),
        "decade": user_prefs.get("decade"), "tags": user_prefs.get("tags"),
    }
    return _score(song_view, prefs_view, strategy)


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5,
                    strategy: ScoringStrategy = DEFAULT_STRATEGY,
                    diversity_penalty: float = 0.0) -> List[Tuple[Dict, float, str]]:
    """Score every song and return the top-k as (song, score, explanation), highest first."""
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song, strategy)
        explanation = "; ".join(reasons) if reasons else "no matches"
        scored.append((song, score, explanation))
    scored.sort(key=lambda item: item[1], reverse=True)
    return _apply_diversity(scored, k, diversity_penalty, get_song=lambda t: t[0])
