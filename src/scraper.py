import os
import json
import time
from dotenv import load_dotenv
import serpapi

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, ".env")
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("API_KEY")
client = serpapi.Client(api_key=api_key)

# Found from the place lookup - identifies this exact KFC branch
DATA_ID = "0x46920fe83f431ac5:0x9645afeacf4bea1a"

all_reviews = []
params = {
    "engine": "google_maps_reviews",
    "data_id": DATA_ID,
    "hl": "en",
}

page = 1
while True:
    print(f"Fetching page {page}...")
    results = client.search(params)

    reviews = results.get("reviews", [])
    if not reviews:
        print("No more reviews found - stopping.")
        break

    all_reviews.extend(reviews)
    print(f"  Got {len(reviews)} reviews (total so far: {len(all_reviews)})")

    # Check if there's a next page
    pagination = results.get("serpapi_pagination", {})
    next_page_token = pagination.get("next_page_token")

    if not next_page_token:
        print("No next_page_token - reached the end.")
        break

    params["next_page_token"] = next_page_token
    page += 1
    time.sleep(1)  # be polite between requests

print(f"\nTotal reviews collected: {len(all_reviews)}")

# Save raw results so stage 2 (cleaning) has something to work with
output_path = os.path.join(project_root, "data", "raw", "raw_reviews.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(all_reviews, f, ensure_ascii=False, indent=2)

print(f"Saved to {output_path}")