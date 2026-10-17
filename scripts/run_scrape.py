"""Download all reviews of one place and save them as raw JSON.

Uses SerpApi credits. Needs API_KEY in the .env file.
"""
import argparse
import os
import sys

import serpapi
from dotenv import load_dotenv

from kfc_absa.config import ENV_PATH, RAW_PATH
from kfc_absa.data_io import save_raw_reviews
from kfc_absa.scraping import fetch_reviews

# Identifies the KFC branch (found from the place lookup)
DEFAULT_DATA_ID = "0x46920fe83f431ac5:0x9645afeacf4bea1a"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-id", default=DEFAULT_DATA_ID, help="Google Maps data_id of the place")
    args = parser.parse_args()

    load_dotenv(dotenv_path=ENV_PATH)
    api_key = os.getenv("API_KEY")
    if not api_key:
        sys.exit(f"API_KEY is empty. Add it to {ENV_PATH} (see .env.example).")

    reviews = fetch_reviews(serpapi.Client(api_key=api_key), args.data_id)
    print(f"\nTotal reviews collected: {len(reviews)}")
    save_raw_reviews(reviews)
    print(f"Saved to {RAW_PATH}")


if __name__ == "__main__":
    main()
