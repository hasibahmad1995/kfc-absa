# KFC ABSA

Aspect-based sentiment analysis of Google Maps reviews for one KFC branch: what do customers like or dislike about the food, the service, the waiting time and so on, beyond a single star rating.

**Status:** data collection and cleaning are done. The sentiment analysis is the next step.

## Data
- 225 reviews of one branch, collected through [SerpApi](https://serpapi.com/)'s Google Maps Reviews API.
- Each review has a star rating, a date, free text, optional detail scores (food, service, atmosphere, wait time, order type, meal type, price per person) and sometimes a reply from the business.
- The reviewer identifier is dropped. The raw JSON is not in the repo; `data/processed/reviews.csv` is.

## How it works
```
SerpApi  ->  data/raw/raw_reviews.json  ->  data/processed/reviews.csv  ->  analysis
 scrape        (not in the repo)             flatten + normalize text
```
1. **Scrape** (`scripts/run_scrape.py`): follows the API's page tokens until the last page and saves the raw answer. Uses SerpApi credits, so it is run once.
2. **Clean** (`scripts/run_clean.py`): flattens each nested review into one row and adds `clean_text` (line breaks, extra spaces and curly quotes normalized). The original `text` is kept next to it. Case, punctuation and emoji are left alone because they can carry sentiment.

Decisions and problems found along the way are written up in [`notebooks/01_exploration.ipynb`](notebooks/01_exploration.ipynb).

## Project layout
```
src/kfc_absa/
    scraping.py     fetch_reviews(client, data_id)
    cleaning.py     flatten_reviews(raw), normalize_text(text)
    profile.py      profile_texts(texts): counts only, never shows review text
    data_io.py      load/save the raw JSON and the CSV
    config.py       paths
scripts/            run_scrape.py, run_clean.py
notebooks/          01_exploration.ipynb
data/               raw/ (git-ignored), processed/reviews.csv
```

## Design rule
Cleaning rules come from standards (Unicode categories) and from parameters, never from reading the data. Optional review fields are discovered from the data. `profile_texts` summarises a text column with counts only, so data you may not read can still be checked.

## Setup
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```
To scrape, copy `.env.example` to `.env` and put your SerpApi key in it:
```
python scripts/run_scrape.py
```
To rebuild the CSV from the raw file:
```
python scripts/run_clean.py
```

## Tests
```
pytest
```

## Roadmap
- [x] Keep emoji intact in `normalize_text`
- [ ] Language detection
- [x] Tests for the cleaning functions
- [ ] Aspect-based sentiment analysis, compared against the star ratings
