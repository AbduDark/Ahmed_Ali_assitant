"""Text cleaning and normalization, especially for Arabic text."""

from __future__ import annotations

import re
import unicodedata


class TextCleaner:
    """Clean and normalize extracted text, with Arabic-specific handling."""

    # Arabic diacritics (tashkeel)
    ARABIC_DIACRITICS = re.compile(r"[\u0617-\u061A\u064B-\u0652\u0670]")

    # Excessive whitespace
    MULTI_SPACES = re.compile(r"[ \t]+")
    MULTI_NEWLINES = re.compile(r"\n{3,}")

    # Common PDF artifacts
    PDF_ARTIFACTS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")

    def clean(self, text: str, *, remove_diacritics: bool = False) -> str:
        """
        Clean and normalize text.

        Args:
            text: Raw extracted text.
            remove_diacritics: Whether to strip Arabic diacritics.

        Returns:
            Cleaned text.
        """
        if not text:
            return ""

        # Remove null bytes and control characters
        text = self.PDF_ARTIFACTS.sub("", text)

        # Unicode normalization (NFKC)
        text = unicodedata.normalize("NFKC", text)

        # Normalize Arabic characters
        text = self._normalize_arabic(text)

        # Optionally remove diacritics
        if remove_diacritics:
            text = self.ARABIC_DIACRITICS.sub("", text)

        # Normalize whitespace
        text = self.MULTI_SPACES.sub(" ", text)
        text = self.MULTI_NEWLINES.sub("\n\n", text)

        # Strip leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split("\n")]
        text = "\n".join(lines)

        return text.strip()

    def _normalize_arabic(self, text: str) -> str:
        """Normalize common Arabic character variations."""
        # Normalize Alef variations
        text = re.sub(r"[إأآا]", "ا", text)

        # Normalize Taa Marbuta / Haa
        # (Keep this off by default — it can change meaning)

        # Normalize Yaa
        text = text.replace("ى", "ي")

        return text

    def clean_for_embedding(self, text: str) -> str:
        """
        Aggressively clean text for embedding generation.

        Removes diacritics, extra formatting, page numbers, etc.
        """
        text = self.clean(text, remove_diacritics=True)

        # Remove standalone numbers (page numbers, etc.)
        text = re.sub(r"^\d+\s*$", "", text, flags=re.MULTILINE)

        # Remove very short lines (likely headers/footers)
        lines = text.split("\n")
        lines = [line for line in lines if len(line.strip()) > 3]
        text = "\n".join(lines)

        return text.strip()
