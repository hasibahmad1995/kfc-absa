"""Turn raw SerpApi review records into a flat, analysis-ready table."""
import re
import unicodedata

import pandas as pd

# Curly quotes -> straight quotes (U+2018/2019 single, U+201C/201D double).
QUOTES = {"\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"'}
# Zero-width characters that carry no text. U+200D (zero-width joiner) is NOT
# listed on purpose: emoji such as the woman facepalming use it to glue pieces together.
INVISIBLE = re.compile(r"[\u200b\u200c\u2060\ufeff]")


def normalize_text(text):
    """Return `text` with consistent quotes and whitespace.

    Case, punctuation and emoji are kept on purpose: they can carry sentiment.
    Missing values (None/NaN) are returned unchanged.
    """
    if not isinstance(text, str):
        return text
    text = unicodedata.normalize("NFC", text)
    text = INVISIBLE.sub("", text)
    for fancy, plain in QUOTES.items():
        text = text.replace(fancy, plain)
    return re.sub(r"\s+", " ", text).strip()  # newlines/tabs/runs of spaces -> one space


def detail_keys(raw_reviews):
    """All field names that appear in the `details` part of any review.

    Google does not give the same fields for every business, so check what
    really exists before relying on a name.
    """
    keys = set()
    for review in raw_reviews:
        keys.update((review.get("details") or {}).keys())
    return keys


def flatten_reviews(raw_reviews):
    """One row per review, with the fields we use. `clean_text` sits next to `text`."""
    rows = []
    for i, review in enumerate(raw_reviews, start=1):
        extracted = review.get("extracted_snippet") or {}
        details = review.get("details") or {}
        response = review.get("response") or {}
        response_extracted = response.get("extracted_snippet") or {}

        rows.append({
            "id": i,  # our own id, not Google's review_id
            "rating": review.get("rating"),
            "iso_date": review.get("iso_date"),
            "text": extracted.get("original") or review.get("snippet"),
            # Per-aspect details: empty when the reviewer did not give them
            "order_type": details.get("order_type"),  # Dine in / Take out / Delivery
            "meal_type": details.get("meal_type"),    # Breakfast / Lunch / Dinner ...
            "price_per_person": details.get("price_per_person"),
            "food": details.get("food"),
            "service": details.get("service"),
            "atmosphere": details.get("atmosphere"),
            "wait_time": details.get("wait_time"),
            # The business's reply, if there is one
            "response_iso_date": response.get("iso_date"),
            "response_text_original": response_extracted.get("original"),
            "response_text_translated": response_extracted.get("translated"),
        })

    df = pd.DataFrame(rows)
    df.insert(df.columns.get_loc("text") + 1, "clean_text", df["text"].map(normalize_text))
    return df
