from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class Settings:
    stats_api: str = "https://statsapi.mlb.com/api/v1"
    savant_csv: str = (
        "https://baseballsavant.mlb.com/leaderboard/custom"
    )
    odds_url: str = (
        "https://api.the-odds-api.com/v4/sports/baseball_mlb/odds"
    )
    odds_api_key: str | None = os.getenv("ODDS_API_KEY")
    cache_dir: Path = Path("data/raw/cache")
