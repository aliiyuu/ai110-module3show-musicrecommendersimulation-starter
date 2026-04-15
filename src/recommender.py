from typing import List, Dict, Tuple
from dataclasses import dataclass
import csv
import math

@dataclass
class Song:
    """
    Represents a song and its attributes.
    """
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
    instrumentalness: float = 0.0   # New: 0–1, instrumental vs. vocal
    liveness: float = 0.0            # New: 0–1, live performance feel
    speechiness: float = 0.0         # New: 0–1, spoken word content

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences with flexibility for discovery.
    Supports multiple genres and moods, and numeric targets for advanced features.
    """
    favorite_genres: List[str]  # e.g., ["rock", "indie pop"] — allows multi-select
    favorite_moods: List[str]   # e.g., ["intense", "happy"] — allows multi-select
    target_energy: float        # 0.0–1.0, user's preferred energy level
    acousticness_preference: float  # 0.0–1.0; 0.5 = neutral, 0 = not acoustic, 1 = very acoustic
    target_instrumentalness: float = 0.5  # 0.0–1.0; how much instrumental vs. vocal
    target_liveness: float = 0.5           # 0.0–1.0; studio-polished vs. live feel
    target_speechiness: float = 0.5        # 0.0–1.0; low = pure music, high = rap/spoken
    discovery_flexibility: float = 0.0     # 0.0–1.0; 0 = strict match, 1 = very open to variety

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        ranked = sorted(
            self.songs,
            key=lambda song: self._score_song(user, song)[0],
            reverse=True,
        )
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        score, reasons = self._score_song(user, song)
        return f"Score {score:.2f}: " + "; ".join(reasons)

    def _score_song(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        """Return a normalized points-based score in [0, 1] and a list of explanation reasons.
        
        WEIGHT SHIFT EXPERIMENT: Genre halved (+2.0→+1.0), Energy doubled (×2.0→×4.0), max_points=7.0.
        """
        genre_match = any(_matches(song.genre, g) for g in user.favorite_genres)
        mood_match = any(_matches(song.mood, m) for m in user.favorite_moods)

        energy_similarity = _gaussian_similarity(song.energy, user.target_energy, sigma=0.18)

        points = 0.0
        points += 1.0 if genre_match else 0.0
        points += 1.0 if mood_match else 0.0
        points += 4.0 * energy_similarity

        acoustic_sim = _gaussian_similarity(song.acousticness, user.acousticness_preference, sigma=0.3)
        instrumental_sim = _gaussian_similarity(song.instrumentalness, user.target_instrumentalness, sigma=0.25)
        liveness_sim = _gaussian_similarity(song.liveness, user.target_liveness, sigma=0.25)
        speechiness_sim = _gaussian_similarity(song.speechiness, user.target_speechiness, sigma=0.25)

        # Keep newer features as light tie-breakers instead of main drivers.
        points += 0.25 * acoustic_sim
        points += 0.25 * instrumental_sim
        points += 0.25 * liveness_sim
        points += 0.25 * speechiness_sim

        max_points = 7.0
        base_score = points / max_points
        
        # Discovery flexibility: adds a small random boost to enable serendipity
        if user.discovery_flexibility > 0:
            flexibility_boost = user.discovery_flexibility * 0.1  # Max 10% boost
            import random
            base_score += random.uniform(0, flexibility_boost)

        reasons: List[str] = []
        if genre_match:
            reasons.append("genre match (+1.0)")
        if mood_match:
            reasons.append("mood match (+1.0)")
        reasons.append(f"energy similarity={energy_similarity:.2f} (+{4.0 * energy_similarity:.2f})")
        if acoustic_sim > 0.7:
            reasons.append(f"acousticness fit (+{0.25 * acoustic_sim:.2f})")
        if instrumental_sim > 0.7:
            reasons.append(f"instrumentalness fit (+{0.25 * instrumental_sim:.2f})")
        if liveness_sim > 0.7:
            reasons.append(f"liveness fit (+{0.25 * liveness_sim:.2f})")
        if speechiness_sim > 0.7:
            reasons.append(f"speechiness fit (+{0.25 * speechiness_sim:.2f})")

        return max(0.0, min(1.0, base_score)), reasons

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file, including extended numeric feature columns."""
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append(
                {
                    "id": int(row["id"]),
                    "title": row["title"],
                    "artist": row["artist"],
                    "genre": row["genre"],
                    "mood": row["mood"],
                    "energy": float(row["energy"]),
                    "tempo_bpm": float(row["tempo_bpm"]),
                    "valence": float(row["valence"]),
                    "danceability": float(row["danceability"]),
                    "acousticness": float(row["acousticness"]),
                    "instrumentalness": float(row.get("instrumentalness", 0.0)),
                    "liveness": float(row.get("liveness", 0.0)),
                    "speechiness": float(row.get("speechiness", 0.0)),
                }
            )
    return songs

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, List[str]]]:
    """Score all songs for a user profile and return the top-k ranked results with reasons.
    
    WEIGHT SHIFT EXPERIMENT: Genre halved (+2.0→+1.0), Energy doubled (×2.0→×4.0), max_points=7.0.
    """
    favorite_genres = [g.strip().lower() for g in str(user_prefs.get("genres", "pop")).split(",") if g.strip()]
    favorite_moods = [m.strip().lower() for m in str(user_prefs.get("moods", "happy")).split(",") if m.strip()]
    target_energy = float(user_prefs.get("energy", 0.5))
    acousticness_pref = float(user_prefs.get("acousticness", 0.5))
    target_instrumental = float(user_prefs.get("instrumentalness", 0.5))
    target_live = float(user_prefs.get("liveness", 0.5))
    target_speech = float(user_prefs.get("speechiness", 0.5))

    def score_song(song: Dict) -> Tuple[float, List[str]]:
        song_genre = str(song.get("genre", "")).strip().lower()
        song_mood = str(song.get("mood", "")).strip().lower()

        genre_match = any(_matches(song_genre, genre) for genre in favorite_genres)
        mood_match = any(_matches(song_mood, mood) for mood in favorite_moods)

        energy_similarity = _gaussian_similarity(float(song.get("energy", 0.0)), target_energy, sigma=0.18)
        acoustic_score = _gaussian_similarity(float(song.get("acousticness", 0.0)), acousticness_pref, sigma=0.3)
        instrumental_score = _gaussian_similarity(float(song.get("instrumentalness", 0.0)), target_instrumental, sigma=0.25)
        liveness_score = _gaussian_similarity(float(song.get("liveness", 0.0)), target_live, sigma=0.25)
        speech_score = _gaussian_similarity(float(song.get("speechiness", 0.0)), target_speech, sigma=0.25)

        points = (
            (1.0 if genre_match else 0.0)
            + (1.0 if mood_match else 0.0)
            + (4.0 * energy_similarity)
            + (0.25 * acoustic_score)
            + (0.25 * instrumental_score)
            + (0.25 * liveness_score)
            + (0.25 * speech_score)
        )

        reasons: List[str] = []
        if genre_match:
            reasons.append("genre match (+1.0)")
        if mood_match:
            reasons.append("mood match (+1.0)")
        reasons.append(f"energy similarity={energy_similarity:.2f} (+{4.0 * energy_similarity:.2f})")
        if float(song.get("speechiness", 0.0)) > 0.4:
            reasons.append("high speech (rap/spoken)")
        if float(song.get("instrumentalness", 0.0)) > 0.7:
            reasons.append("very instrumental")

        return points / 7.0, reasons

    scored = [
        (song, *score_song(song))
        for song in songs
    ]
    return sorted(scored, key=lambda item: item[1], reverse=True)[:k]


def _matches(a: str, b: str) -> bool:
    return str(a).strip().lower() == str(b).strip().lower()


def _gaussian_similarity(value: float, target: float, sigma: float) -> float:
    if sigma <= 0:
        return 1.0 if value == target else 0.0
    exponent = -((value - target) ** 2) / (2 * (sigma ** 2))
    return max(0.0, min(1.0, math.exp(exponent)))

