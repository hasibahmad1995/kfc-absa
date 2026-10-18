"""Summarise a text column without showing any of its content.

Use this on data you are not allowed to read: it returns counts only, so the
cleaning rules can be chosen from the summary.
"""
import unicodedata
from collections import Counter

from kfc_absa.cleaning import KEEP_FORMAT_CHARS, _is_invisible_junk, normalize_text


def profile_texts(texts, keep=KEEP_FORMAT_CHARS, short_chars=20):
    """Counts about `texts`. Never returns any review text."""
    texts = list(texts)
    strings = [t for t in texts if isinstance(t, str)]
    categories = Counter()
    removable = 0
    for text in strings:
        categories.update(unicodedata.category(ch) for ch in text)
        removable += any(_is_invisible_junk(ch, keep) for ch in text)
    cleaned = [normalize_text(t, keep) for t in strings]
    return {
        "texts": len(texts),
        "missing": len(texts) - len(strings),
        "empty_after_cleaning": sum(not c for c in cleaned),
        "short_after_cleaning": sum(0 < len(c) < short_chars for c in cleaned),
        "changed_by_cleaning": sum(a != b for a, b in zip(strings, cleaned)),
        "texts_with_invisible_junk": removable,
        "characters_by_unicode_category": dict(categories.most_common()),
    }
