"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("../data/songs.csv")  # Updated to match file path
    print(f"Loaded: {len(songs)} songs")

    # Distinct user profiles for simulation scenarios.
    user_profiles = {
        "High-Energy Pop": {
            "genres": "pop,electronic,indie pop",
            "moods": "happy,energetic,playful",
            "energy": 0.9,
            "acousticness": 0.2,
            "instrumentalness": 0.2,
            "liveness": 0.4,
            "speechiness": 0.2,
        },
        "Chill Lofi": {
            "genres": "lofi,ambient,jazz",
            "moods": "chill,focused,relaxed",
            "energy": 0.35,
            "acousticness": 0.8,
            "instrumentalness": 0.85,
            "liveness": 0.2,
            "speechiness": 0.05,
        },
        "Deep Intense Rock": {
            "genres": "rock,metal",
            "moods": "intense,moody",
            "energy": 0.95,
            "acousticness": 0.1,
            "instrumentalness": 0.3,
            "liveness": 0.6,
            "speechiness": 0.1,
        },
    }

    # Edge-case profiles to stress-test scoring behavior.
    edge_case_profiles = {
        "No Clear Genre or Mood": {
            "genres": "",
            "moods": "",
            "energy": 0.5,
            "acousticness": 0.5,
            "instrumentalness": 0.5,
            "liveness": 0.5,
            "speechiness": 0.5,
        },
        "Unknown Preferences": {
            "genres": "k-pop,drill,afrobeats",
            "moods": "euphoric,chaotic",
            "energy": 0.7,
            "acousticness": 0.3,
            "instrumentalness": 0.4,
            "liveness": 0.4,
            "speechiness": 0.4,
        },
        "Conflicting Signals": {
            "genres": "metal,ambient",
            "moods": "chill,intense",
            "energy": 0.95,
            "acousticness": 0.9,
            "instrumentalness": 0.9,
            "liveness": 0.1,
            "speechiness": 0.8,
        },
        "Out-of-Range Energy": {
            "genres": "pop",
            "moods": "happy",
            "energy": 1.5,
            "acousticness": 0.2,
            "instrumentalness": 0.2,
            "liveness": 0.3,
            "speechiness": 0.2,
        },
    }

    for profile_name, user_prefs in user_profiles.items():
        recommendations = recommend_songs(user_prefs, songs, k=5)

        print(f"\nTop recommendations for {profile_name}:\n")
        for rec in recommendations:
            song, score, reasons = rec
            print(f"{song['title']} - Score: {score:.2f}")
            print("Because:")
            for reason in reasons:
                print(f"- {reason}")
            print()

    print("\n=== Edge-Case Profiles ===")
    for profile_name, user_prefs in edge_case_profiles.items():
        recommendations = recommend_songs(user_prefs, songs, k=5)

        print(f"\nTop recommendations for {profile_name}:\n")
        for rec in recommendations:
            song, score, reasons = rec
            print(f"{song['title']} - Score: {score:.2f}")
            print("Because:")
            for reason in reasons:
                print(f"- {reason}")
            print()


if __name__ == "__main__":
    main()
