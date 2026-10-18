"""Tests for profile_texts. Texts here are made up."""
from kfc_absa.profile import profile_texts


def test_counts_are_reported():
    texts = ["fine", "cold\N{ZERO WIDTH SPACE}fries here and more", "", None]
    report = profile_texts(texts)
    assert report["texts"] == 4
    assert report["missing"] == 1
    assert report["empty_after_cleaning"] == 1
    assert report["texts_with_invisible_junk"] == 1
    assert report["changed_by_cleaning"] == 1
    assert report["short_after_cleaning"] == 1


def test_report_contains_no_review_text():
    secret = "my-private-sentence"
    report = profile_texts([secret])
    assert secret not in str(report)
