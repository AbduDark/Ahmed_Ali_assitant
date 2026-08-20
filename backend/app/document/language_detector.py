"""Language detection using character analysis."""

from __future__ import annotations

import re


# Unicode ranges
ARABIC_PATTERN = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]")
LATIN_PATTERN = re.compile(r"[a-zA-Z]")


def detect_language(text: str) -> str:
    """
    Detect the primary language of text.

    Returns:
        "ar" for Arabic, "en" for English, "mixed" for mixed content.
    """
    if not text or len(text.strip()) < 5:
        return "ar"  # Default to Arabic

    arabic_count = len(ARABIC_PATTERN.findall(text))
    latin_count = len(LATIN_PATTERN.findall(text))
    total = arabic_count + latin_count

    if total == 0:
        return "ar"

    arabic_ratio = arabic_count / total

    if arabic_ratio > 0.7:
        return "ar"
    elif arabic_ratio < 0.3:
        return "en"
    else:
        return "mixed"
