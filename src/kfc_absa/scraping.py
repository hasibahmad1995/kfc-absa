"""Fetch Google Maps reviews for one place through the SerpApi client."""
import time


def fetch_reviews(client, data_id, pause=1.0, language="en"):
    """Return every review for the place `data_id`, following the page tokens.

    Each request asks for one page. The answer carries a `next_page_token`
    for the following page; no token (or an empty page) means we are done.
    Reviews are only held in memory, the caller is responsible for saving them.
    """
    params = {
        "engine": "google_maps_reviews",
        "data_id": data_id,
        "hl": language,
    }

    all_reviews = []
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

        next_page_token = results.get("serpapi_pagination", {}).get("next_page_token")
        if not next_page_token:
            print("No next_page_token - reached the end.")
            break

        params["next_page_token"] = next_page_token
        page += 1
        time.sleep(pause)

    return all_reviews
