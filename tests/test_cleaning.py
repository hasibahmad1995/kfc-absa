"""Tests for the cleaning functions. Reviews here are made up."""
import pandas as pd

from kfc_absa.cleaning import detail_keys, flatten_reviews, normalize_text

FACEPALM = "\U0001F926\u200d\u2640\ufe0f"  # face palm + zero-width joiner + female sign


# --- normalize_text -------------------------------------------------------

def test_whitespace_runs_become_one_space_and_ends_are_trimmed():
    assert normalize_text("  great\n\nfood \t here \n") == "great food here"


def test_curly_quotes_become_straight():
    assert normalize_text("it\u2019s \u201cfine\u201d") == "it's \"fine\""


def test_zero_width_space_is_removed():
    assert normalize_text("cold\u200b fries") == "cold fries"


def test_emoji_joiner_is_kept_so_the_emoji_stays_whole():
    assert normalize_text(f"so bad {FACEPALM}") == f"so bad {FACEPALM}"


def test_case_and_emoji_are_kept():
    assert normalize_text("NOT GOOD \U0001F621") == "NOT GOOD \U0001F621"


def test_missing_values_pass_through():
    assert normalize_text(None) is None
    assert pd.isna(normalize_text(float("nan")))


# --- flatten_reviews ------------------------------------------------------

def make_review(**overrides):
    review = {
        "rating": 4,
        "iso_date": "2026-01-01T10:00:00Z",
        "extracted_snippet": {"original": "Good\nfood"},
        "details": {
            "order_type": "Take out",
            "meal_type": "Lunch",
            "food": 5,
            "service": 3,
        },
        "response": {
            "iso_date": "2026-01-02T10:00:00Z",
            "extracted_snippet": {"original": "Kiitos", "translated": "Thanks"},
        },
    }
    review.update(overrides)
    return review


def test_order_type_and_meal_type_are_separate_columns():
    df = flatten_reviews([make_review()])
    assert df.loc[0, "order_type"] == "Take out"
    assert df.loc[0, "meal_type"] == "Lunch"


def test_clean_text_sits_right_after_text_and_text_is_unchanged():
    df = flatten_reviews([make_review()])
    cols = list(df.columns)
    assert cols.index("clean_text") == cols.index("text") + 1
    assert df.loc[0, "text"] == "Good\nfood"
    assert df.loc[0, "clean_text"] == "Good food"


def test_text_falls_back_to_snippet():
    review = make_review(extracted_snippet={}, snippet="from snippet")
    assert flatten_reviews([review]).loc[0, "text"] == "from snippet"


def test_review_without_details_or_response_still_works():
    review = {"rating": 1, "iso_date": "2026-01-01T10:00:00Z", "snippet": "meh"}
    df = flatten_reviews([review])
    assert df.loc[0, "text"] == "meh"
    assert pd.isna(df.loc[0, "order_type"])
    assert pd.isna(df.loc[0, "response_text_original"])


def test_reply_and_its_translation_are_copied():
    df = flatten_reviews([make_review()])
    assert df.loc[0, "response_text_original"] == "Kiitos"
    assert df.loc[0, "response_text_translated"] == "Thanks"


def test_ids_start_at_one_and_there_is_no_reviewer_identifier():
    df = flatten_reviews([make_review(), make_review()])
    assert df["id"].tolist() == [1, 2]
    assert "contributor_id" not in df.columns


# --- detail_keys ----------------------------------------------------------

def test_detail_keys_collects_every_key_seen():
    reviews = [make_review(), {"details": {"wait_time": "5 min"}}, {"details": None}, {}]
    assert detail_keys(reviews) == {"order_type", "meal_type", "food", "service", "wait_time"}
