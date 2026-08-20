"""PDF text extraction using PyMuPDF."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import fitz  # PyMuPDF

from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class PageContent:
    """Extracted content from a single page."""
    page_number: int
    text: str
    has_images: bool = False


@dataclass
class ExtractedDocument:
    """Full extracted document content."""
    pages: list[PageContent] = field(default_factory=list)
    total_pages: int = 0
    metadata: dict = field(default_factory=dict)

    @property
    def full_text(self) -> str:
        return "\n\n".join(page.text for page in self.pages if page.text.strip())


class PDFExtractor:
    """Extract text from PDF files using PyMuPDF."""

    def extract(self, file_path: str | Path) -> ExtractedDocument:
        """
        Extract text from a PDF file.

        Returns an ExtractedDocument with per-page content.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        logger.info(f"Extracting text from PDF: {file_path.name}")

        doc = fitz.open(str(file_path))
        pages: list[PageContent] = []

        try:
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text")

                # Check if page has images (might need OCR later)
                image_list = page.get_images(full=True)
                has_images = len(image_list) > 0

                pages.append(PageContent(
                    page_number=page_num + 1,  # 1-indexed
                    text=text.strip(),
                    has_images=has_images,
                ))

            # Extract document metadata
            metadata = dict(doc.metadata) if doc.metadata else {}

            result = ExtractedDocument(
                pages=pages,
                total_pages=len(doc),
                metadata=metadata,
            )

            non_empty_pages = sum(1 for p in pages if p.text.strip())
            logger.info(
                f"Extracted {non_empty_pages}/{len(doc)} pages from {file_path.name}"
            )

            return result

        finally:
            doc.close()

    def extract_from_bytes(self, data: bytes, filename: str = "document.pdf") -> ExtractedDocument:
        """Extract text from PDF bytes (useful for in-memory processing)."""
        doc = fitz.open(stream=data, filetype="pdf")
        pages: list[PageContent] = []

        try:
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text")
                image_list = page.get_images(full=True)

                pages.append(PageContent(
                    page_number=page_num + 1,
                    text=text.strip(),
                    has_images=len(image_list) > 0,
                ))

            return ExtractedDocument(
                pages=pages,
                total_pages=len(doc),
                metadata=dict(doc.metadata) if doc.metadata else {},
            )
        finally:
            doc.close()
