"""Turn raw SerpApi review records into a flat, analysis-ready table."""
import re
import unicodedata

import pandas as pd

# Typographic quotes -> straight quotes. A fixed fact about Unicode, not taken from
# any dataset. Guillemets are left alone: they are real quotes in some languages.
QUOTES = {
    "\N{LEFT SINGLE QUOTATION MARK}": "'",
    "\N{RIGHT SINGLE QUOTATION MARK}": "'",
    "\N{SINGLE LOW-9 QUOTATION MARK}": "'",
    "\N{SINGLE HIGH-REVERSED-9 QUOTATION MARK}": "'",
    "\N{LEFT DOUBLE QUOTATION MARK}": '"',
    "\N{RIGHT DOUBLE QUOTATION MARK}": '"',
    "\N{DOUBLE LOW-9 QUOTATION MARK}": '"',
    "\N{DOUBLE HIGH-REVERSED-9 QUOTATION MARK}": '"',
}
QUOTE_TABLE = str.maketrans(QUOTES)

# Invisible "format" characters (Unicode category Cf) are removed, except the
# ones that change how neighbouring characters are drawn. The joiner glues
# emoji together (family, profession, ...); both joiners shape letters in some
# scripts, so text in other languages keeps its meaning.
KEEP_FORMAT_CHARS = frozenset({
    "\N{ZERO WIDTH JOINER}",
    "\N{ZERO WIDTH NON-JOINER}",
})
# Emoji tag sequences (e.g. the flag of England) are also category Cf.
EMOJI_TAG_RANGE = range(0xE0020, 0xE0080)


def _is_invisible_junk(ch, keep):
    """True for invisible characters that carry no text."""
    if ch in keep or ord(ch) in EMOJI_TAG_RANGE:
        return False
    category = unicodedata.category(ch)
    if category == "Cf":  # zero-width space, word joiner, BOM, soft hyphen, bidi marks...
        return True
    return category == "Cc" and not ch.isspace()  # control characters, but not \n or \t


def normalize_text(text, keep=KEEP_FORMAT_CHARS, quote_table=QUOTE_TABLE):
    """Return `text` with consistent quotes, no invisible junk and tidy whitespace.

    Case, punctuation and emoji are kept on purpose: they can carry sentiment.
    Missing values (None/NaN) are returned unchanged.
    """
    if not isinstance(text, str):
        return text
    text = unicodedata.normalize("NFC", text)
    text = "".join(ch for ch in text if not _is_invisible_junk(ch, keep))
    text = text.translate(quote_table)
    return re.sub(r"\s+", " ", text).strip()  # newlines/tabs/runs of spaces -> one space


def detail_keys(raw_reviews):
    """Field names that appear in the `details` part of any review, in the order first seen."""
    keys = {}
    for review in raw_reviews:
        for key in (review.get("details") or {}):
            keys.setdefault(key, None)
    return list(keys)


def flatten_reviews(raw_reviews, detail_fields=None):
    """One row per review. `clean_text` sits next to `text`.

    Google gives different optional details (food, service, ...) for different
    businesses. By default every field found in the data becomes a column.
    Pass `detail_fields` to choose columns yourself.
    """
    if detail_fields is None:
        detail_fields = detail_keys(raw_reviews)
    rows = []
    for i, review in enumerate(raw_reviews, start=1):
        extracted = review.get("extracted_snippet") or {}
        details = review.get("details") or {}
        response = review.get("response") or {}
        response_extracted = response.get("extracted_snippet") or {}

        row = {
            "id": i,  # our own id, not Google's review_id
            "rating": review.get("rating"),
            "iso_date": review.get("iso_date"),
            "text": extracted.get("original") or review.get("snippet"),
        }
        for field in detail_fields:
            row[field] = details.get(field)  # empty when the reviewer did not give it
        # The business's reply, if there is one
        row["response_iso_date"] = response.get("iso_date")
        row["response_text_original"] = response_extracted.get("original")
        row["response_text_translated"] = response_extracted.get("translated")
        rows.append(row)

    df = pd.DataFrame(rows)
    df.insert(df.columns.get_loc("text") + 1, "clean_text", df["text"].map(normalize_text))
    return df
