from src.recommender import Song, UserProfile, Recommender

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
            instrumentalness=0.05,
            liveness=0.20,
            speechiness=0.03,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
            instrumentalness=0.80,
            liveness=0.10,
            speechiness=0.02,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genres=["pop"],
        favorite_moods=["happy"],
        target_energy=0.8,
        acousticness_preference=0.2,
        target_instrumentalness=0.1,
        target_liveness=0.2,
        target_speechiness=0.05,
        discovery_flexibility=0.0,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Pop, happy, high energy track should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genres=["pop"],
        favorite_moods=["happy"],
        target_energy=0.8,
        acousticness_preference=0.2,
        target_instrumentalness=0.1,
        target_liveness=0.2,
        target_speechiness=0.05,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""
    assert "Score" in explanation


def test_multi_genre_preference():
    """Test that users can prefer multiple genres."""
    user = UserProfile(
        favorite_genres=["pop", "lofi"],
        favorite_moods=["happy", "chill"],
        target_energy=0.6,
        acousticness_preference=0.5,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)
    
    assert len(results) == 2
    # Both songs should score well now (each matches at least one genre and mood)


def test_genre_match_counts_more_than_mood_match():
    songs = [
        Song(
            id=101,
            title="Genre Match Only",
            artist="A",
            genre="rock",
            mood="sad",
            energy=0.8,
            tempo_bpm=120,
            valence=0.5,
            danceability=0.5,
            acousticness=0.5,
            instrumentalness=0.5,
            liveness=0.5,
            speechiness=0.5,
        ),
        Song(
            id=102,
            title="Mood Match Only",
            artist="B",
            genre="jazz",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.5,
            danceability=0.5,
            acousticness=0.5,
            instrumentalness=0.5,
            liveness=0.5,
            speechiness=0.5,
        ),
    ]
    rec = Recommender(songs)

    user = UserProfile(
        favorite_genres=["rock"],
        favorite_moods=["happy"],
        target_energy=0.8,
        acousticness_preference=0.5,
        target_instrumentalness=0.5,
        target_liveness=0.5,
        target_speechiness=0.5,
    )

    ranked = rec.recommend(user, k=2)
    assert ranked[0].title == "Genre Match Only"

