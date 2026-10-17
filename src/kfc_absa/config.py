"""Project-wide paths."""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ENV_PATH = PROJECT_ROOT / ".env"
RAW_PATH = PROJECT_ROOT / "data" / "raw" / "raw_reviews.json"
PROCESSED_PATH = PROJECT_ROOT / "data" / "processed" / "reviews.csv"
