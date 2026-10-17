# KFC ABSA

Aspect-based sentiment analysis of Google Maps reviews for a KFC branch.

## Setup
    python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt

Create a `.env` file in the project root:

    API_KEY=<your SerpApi key>

## Pipeline
1. `python src/scraper.py` - fetch reviews -> `data/raw/raw_reviews.json`
2. `python src/clean_reviews.py` - flatten to `data/processed/reviews.csv`
3. `notebooks/checking_data.ipynb` - data exploration
