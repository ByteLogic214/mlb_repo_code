import argparse
import json
from pathlib import Path

from ..config import Settings
from .client import CachedClient


def extract_daily(day, output_dir):
    settings = Settings()
    client = CachedClient(settings.cache_dir)

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    schedule_url = f"{settings.stats_api}/schedule"

    schedule = client.json(
        schedule_url,
        params={
            "sportId": 1,
            "date": day,
            "hydrate": "venue,weather,probablePitcher",
        },
    )

    games = []
    play_by_play = []
    boxscores = []

    for schedule_day in schedule.get("dates", []):
        for game in schedule_day.get("games", []):
            game_pk = game["gamePk"]
            games.append(game)

            pbp_url = (
                f"{settings.stats_api}/game/"
                f"{game_pk}/playByPlay"
            )
            boxscore_url = (
                f"{settings.stats_api}/game/"
                f"{game_pk}/boxscore"
            )

            play_by_play.append(
                client.json(pbp_url)
            )
            boxscores.append(
                client.json(boxscore_url)
            )

    (output / f"schedule_{day}.json").write_text(
        json.dumps(games)
    )

    (output / f"pbp_{day}.json").write_text(
        json.dumps(play_by_play)
    )

    (output / f"boxscore_{day}.json").write_text(
        json.dumps(boxscores)
    )

    statcast_params = {
        "type": "details",
        "year": day[:4],
        "start_date": day,
        "end_date": day,
        "csv": "true",
        "sort": "pitches",
        "sortDir": "desc",
    }

    statcast = client.csv(
        settings.savant_csv,
        statcast_params,
    )

    statcast.to_csv(
        output / f"statcast_{day}.csv",
        index=False,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    parser.add_argument(
        "--output-dir",
        default="data/raw/daily",
    )

    args = parser.parse_args()
    extract_daily(args.date, args.output_dir)


if __name__ == "__main__":
    main()
