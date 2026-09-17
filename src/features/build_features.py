import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def build_daily_features(day, input_dir):
    root = Path(input_dir)
    schedule_path = root / f"schedule_{day}.json"

    games = json.loads(schedule_path.read_text())
    rows = []

    for game in games:
        home = game["teams"]["home"]
        away = game["teams"]["away"]
        weather = game.get("weather", {})

        rows.append(
            {
                "game_id": game["gamePk"],
                "game_date": day,
                "home_team": home["team"]["abbreviation"],
                "away_team": away["team"]["abbreviation"],
                "home_win": int(home.get("isWinner", False)),
                "total_runs": (
                    home.get("score", 0)
                    + away.get("score", 0)
                ),
                "home_siera": np.nan,
                "away_siera": np.nan,
                "home_xfip": np.nan,
                "away_xfip": np.nan,
                "home_xera": np.nan,
                "away_xera": np.nan,
                "home_park_factor": np.nan,
                "away_park_factor": np.nan,
                "home_weather_temp": weather.get("temp"),
                "home_weather_wind_speed": weather.get("wind"),
                "home_weather_condition": weather.get(
                    "condition"
                ),
            }
        )

    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    parser.add_argument(
        "--input-dir",
        default="data/raw/daily",
    )
    parser.add_argument("--output-file", required=True)

    args = parser.parse_args()

    features = build_daily_features(
        args.date,
        args.input_dir,
    )

    output = Path(args.output_file)
    output.parent.mkdir(parents=True, exist_ok=True)

    features.to_parquet(output, index=False)


if __name__ == "__main__":
    main()
