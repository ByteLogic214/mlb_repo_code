import argparse
from pathlib import Path

import joblib
import pandas as pd


def load_models(models_dir):
    root = Path(models_dir)

    return {
        "random_forest": joblib.load(
            root / "random_forest" / "model.joblib"
        ),
        "svm": joblib.load(
            root / "svm" / "model.joblib"
        ),
    }


def generate_predictions(
    date,
    models_dir,
    features_file,
    output_dir,
):
    features = pd.read_parquet(features_file)

    excluded = [
        "game_id",
        "game_date",
        "home_win",
        "total_runs",
    ]

    feature_columns = [
        col for col in features.columns
        if col not in excluded
    ]

    X = features[feature_columns]
    models = load_models(models_dir)

    rf_probability = models[
        "random_forest"
    ].predict_proba(X)[:, 1]

    svm_probability = models[
        "svm"
    ].predict_proba(X)[:, 1]

    result = features[
        [
            "game_id",
            "game_date",
            "home_team",
            "away_team",
        ]
    ].copy()

    result["home_win_probability"] = (
        rf_probability + svm_probability
    ) / 2

    result["away_win_probability"] = (
        1 - result["home_win_probability"]
    )

    result["model_version"] = "production"

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    destination = output / f"predictions_{date}.csv"
    result.to_csv(destination, index=False)

    return destination


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    parser.add_argument("--models-dir", required=True)
    parser.add_argument("--features-file", required=True)
    parser.add_argument("--output-dir", required=True)

    args = parser.parse_args()

    generate_predictions(
        date=args.date,
        models_dir=args.models_dir,
        features_file=args.features_file,
        output_dir=args.output_dir,
    )


if __name__ == "__main__":
    main()
