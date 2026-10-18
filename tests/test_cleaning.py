"""Tests for the cleaning functions. Reviews here are made up."""
import unicodedata

import pandas as pd

from kfc_absa.cleaning import detail_keys, flatten_reviews, normalize_text

ZWJ = "\N{ZERO WIDTH JOINER}"
FACEPALM = "\N{FACE PALM}" + ZWJ + "\N{FEMALE SIGN}\N{VARIATION SELECTOR-16}"
FAMILY = "\N{MAN}" + ZWJ + "\N{WOMAN}" + ZWJ + "\N{GIRL}"
ENGLAND_FLAG = "\N{WAVING BLACK FLAG}" + "".join(chr(c) for c in (0xE0067, 0xE0062, 0xE0065, 0xE006E, 0xE0067, 0xE007F))


# --- normalize_text -------------------------------------------------------

def test_whitespace_runs_become_one_space_and_ends_are_trimmed():
    assert normalize_text("  great\n\nfood \t here \n") == "great food here"


def test_typographic_quotes_become_straight():
    text = "it\N{RIGHT SINGLE QUOTATION MARK}s \N{LEFT DOUBLE QUOTATION MARK}fine\N{RIGHT DOUBLE QUOTATION MARK}"
    assert normalize_text(text) == "it's \"fine\""


def test_invisible_format_characters_are_removed_by_category():
    # None of these are named in the code; they are all category Cf.
    for name in ("ZERO WIDTH SPACE", "WORD JOINER", "ZERO WIDTH NO-BREAK SPACE",
                 "SOFT HYPHEN", "LEFT-TO-RIGHT MARK", "RIGHT-TO-LEFT MARK"):
        assert normalize_text("cold" + unicodedata.lookup(name) + " fries") == "cold fries", name


def test_control_characters_are_removed():
    assert normalize_text("a\x00b\x07c") == "abc"


def test_no_break_space_becomes_a_normal_space():
    assert normalize_text("a\N{NO-BREAK SPACE}b") == "a b"


def test_emoji_sequences_stay_whole():
    for emoji in (FACEPALM, FAMILY, ENGLAND_FLAG):
        assert normalize_text(f"so bad {emoji}") == f"so bad {emoji}"


def test_quote_mapping_can_be_changed():
    assert normalize_text("it’s", quote_table={}) == "it’s"


def test_what_to_keep_can_be_changed():
    assert normalize_text(f"a{ZWJ}b", keep=frozenset()) == "ab"


def test_case_and_emoji_are_kept():
    assert normalize_text("NOT GOOD \N{POUTING FACE}") == "NOT GOOD \N{POUTING FACE}"


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
    assert "order_type" not in df.columns  # nothing in the data, so no column
    assert pd.isna(df.loc[0, "response_text_original"])


def test_reply_and_its_translation_are_copied():
    df = flatten_reviews([make_review()])
    assert df.loc[0, "response_text_original"] == "Kiitos"
    assert df.loc[0, "response_text_translated"] == "Thanks"


def test_detail_fields_are_discovered_from_the_data_by_default():
    review = make_review(details={"rooms": 4, "cleanliness": 5})
    df = flatten_reviews([review])
    assert df.loc[0, "rooms"] == 4 and df.loc[0, "cleanliness"] == 5
    assert "food" not in df.columns


def test_detail_fields_are_a_parameter():
    review = make_review(details={"food": 5, "noise_level": "Quiet"})
    df = flatten_reviews([review], detail_fields=("noise_level", "food"))
    assert list(df.columns)[5:7] == ["noise_level", "food"]
    assert df.loc[0, "noise_level"] == "Quiet"
    assert "order_type" not in df.columns


def test_ids_start_at_one_and_there_is_no_reviewer_identifier():
    df = flatten_reviews([make_review(), make_review()])
    assert df["id"].tolist() == [1, 2]
    assert "contributor_id" not in df.columns


# --- detail_keys ----------------------------------------------------------

def test_detail_keys_collects_every_key_seen():
    reviews = [make_review(), {"details": {"wait_time": "5 min"}}, {"details": None}, {}]
    assert detail_keys(reviews) == ["order_type", "meal_type", "food", "service", "wait_time"]
