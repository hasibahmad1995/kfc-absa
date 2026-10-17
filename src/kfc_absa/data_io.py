"""Read and write the raw JSON and the processed CSV."""
import json

import pandas as pd

from kfc_absa.config import PROCESSED_PATH, RAW_PATH


def load_raw_reviews(path=RAW_PATH):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_raw_reviews(reviews, path=RAW_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(reviews, f, ensure_ascii=False, indent=2)


def load_reviews(path=PROCESSED_PATH):
    return pd.read_csv(path)


def save_reviews(df, path=PROCESSED_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
