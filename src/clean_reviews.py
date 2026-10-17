import os
import re
import json
import unicodedata
import pandas as pd

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
input_path = os.path.join(project_root, "data", "raw", "raw_reviews.json")

with open(input_path, "r", encoding="utf-8") as f:
    raw_reviews = json.load(f)

print(f"Loaded {len(raw_reviews)} raw reviews")

# --- Step 1: discover what keys actually exist inside "details" ---
# Google doesn't use the same field set for every business, so we check
# what's really there before assuming field names like "wait_time" exist
all_detail_keys = set()
for review in raw_reviews:
    details = review.get("details")
    if details:
        all_detail_keys.update(details.keys())

print(f"\nActual keys found inside 'details' across all reviews:")
print(sorted(all_detail_keys))
print("\n^ Check this list. If 'wait_time' isn't in it, Google isn't giving "
      "it to us as a structured field for this business - it may only "
      "appear as free text inside review comments instead.")

# --- Step 2: build the DataFrame with your requested fields ---
rows = []
for i, review in enumerate(raw_reviews, start=1):
    extracted = review.get("extracted_snippet", {})
    details = review.get("details", {}) or {}
    response = review.get("response", {}) or {}
    response_extracted = response.get("extracted_snippet", {}) or {}

    rows.append({
        "id": i,  # our own auto-incrementing id, not Google's review_id
        "rating": review.get("rating"),
        "iso_date": review.get("iso_date"),
        "text": extracted.get("original") or review.get("snippet"),

        # Per-aspect details - will be None if this specific review
        # didn't include that field, or if Google doesn't track it
        # for this business at all
        "order_type": details.get("order_type"),
        "meal_type": details.get("meal_type"),
        "price_per_person": details.get("price_per_person"),
        "food": details.get("food"),
        "service": details.get("service"),
        "atmosphere": details.get("atmosphere"),
        "wait_time": details.get("wait_time"),  # may not exist - see step 1 output

        # Business response to the review, if one exists
        "response_iso_date": response.get("iso_date"),
        "response_text_original": response_extracted.get("original"),
        "response_text_translated": response_extracted.get("translated"),
    })

df = pd.DataFrame(rows)

# --- Step 3: normalize review text ---
# Keeps the original "text" untouched and adds "clean_text" next to it.
# Case is kept on purpose (CAPS carry sentiment) and nothing is deleted.
QUOTES = {"‘": "'", "’": "'", "“": '"', "”": '"'}
INVISIBLE = re.compile(r"[​‌‍⁠﻿]")


def normalize_text(text):
    if not isinstance(text, str):
        return text
    text = unicodedata.normalize("NFC", text)
    text = INVISIBLE.sub("", text)
    for fancy, plain in QUOTES.items():
        text = text.replace(fancy, plain)
    return re.sub(r"\s+", " ", text).strip()  # newlines/tabs/runs of spaces -> one space


df.insert(df.columns.get_loc("text") + 1, "clean_text", df["text"].map(normalize_text))

print(f"\nDataFrame shape: {df.shape}")
print(df.head())

print(f"\nNon-null counts per column:")
print(df.count())

output_path = os.path.join(project_root, "data", "processed", "reviews.csv")
df.to_csv(output_path, index=False)
print(f"\nSaved to {output_path}")