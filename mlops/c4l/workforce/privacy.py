"""Data minimization preflight. Heuristics are conservative, not complete PII detection."""

import re
import unicodedata


def normalized(text: str) -> str:
    return unicodedata.normalize("NFKC", text).casefold()


def contains_sensitive(text: str) -> bool:
    value = normalized(text)
    patterns = [
        r"(?<!\d)(?:\d[\s-]*){9,}(?!\d)",
        r"\b(?:ssn|social security|routing|bank account|account number|driver.?s? licen[sc]e|passport|claim id|case id|id number|id)\b\s*(?:is|:|#|=)?\s*[a-z-]*\d{3,}",
        r"\b(?:sk-[a-z0-9_-]{12,}|akia[a-z0-9]{16})\b",
    ]
    return any(re.search(pattern, value) for pattern in patterns)
