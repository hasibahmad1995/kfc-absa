"""Flatten the raw reviews into data/processed/reviews.csv."""
from kfc_absa.cleaning import flatten_reviews
from kfc_absa.config import PROCESSED_PATH
from kfc_absa.data_io import load_raw_reviews, save_reviews


def main():
    raw = load_raw_reviews()
    print(f"Loaded {len(raw)} raw reviews")

    df = flatten_reviews(raw)
    print(f"DataFrame shape: {df.shape}")
    print("\nNon-null counts per column:")
    print(df.count())

    save_reviews(df)
    print(f"\nSaved to {PROCESSED_PATH}")


if __name__ == "__main__":
    main()
