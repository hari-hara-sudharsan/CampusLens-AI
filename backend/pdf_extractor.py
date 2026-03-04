"""
CampusLens AI — PDF Extraction Module (Day 2)
=============================================
Multi-strategy PDF text extraction with rich fallback handling.
Handles: normal PDFs, scanned PDFs, corrupt PDFs, password-protected,
multi-column layouts, tables, and embedded text.
"""

import io
import re
from dataclasses import dataclass
from typing import Optional
import pdfplumber


@dataclass
class ExtractionResult:
    """Result of PDF text extraction attempt."""
    text: str
    page_count: int
    char_count: int
    method: str                    # which strategy worked
    quality: str                   # "good" | "partial" | "poor"
    warnings: list[str]
    is_usable: bool


def clean_extracted_text(text: str) -> str:
    """
    Clean raw extracted PDF text:
    - Remove excessive whitespace/blank lines
    - Fix broken hyphenation (word- \nbreaks)
    - Normalize unicode dashes and quotes
    - Remove page headers/footers patterns
    """
    if not text:
        return ""

    # Fix hyphenated line breaks: "assign-\nment" → "assignment"
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Collapse 3+ blank lines into 2
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove lines that look like page numbers only: "- 3 -" or "Page 3 of 10"
    text = re.sub(r"(?m)^[-–—]?\s*\d+\s*[-–—]?\s*$", "", text)
    text = re.sub(r"(?m)^[Pp]age\s+\d+\s+of\s+\d+\s*$", "", text)

    # Normalize unicode quotes and dashes
    text = text.replace("\u2019", "'").replace("\u2018", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2013", "-").replace("\u2014", "-")

    # Collapse excessive spaces
    text = re.sub(r"[ \t]{2,}", " ", text)

    return text.strip()


def assess_text_quality(text: str, page_count: int) -> tuple[str, list[str]]:
    """
    Assess quality of extracted text.
    Returns (quality_label, list_of_warnings).
    """
    warnings = []
    char_count = len(text.strip())
    chars_per_page = char_count / max(page_count, 1)

    # Check for common scanned-PDF artifacts
    gibberish_ratio = len(re.findall(r"[^\x00-\x7F]", text)) / max(char_count, 1)
    if gibberish_ratio > 0.15:
        warnings.append("High proportion of non-ASCII characters — may be OCR noise.")

    # Very few characters per page
    if chars_per_page < 100:
        warnings.append(
            f"Only {chars_per_page:.0f} chars/page extracted. "
            "PDF may be scanned/image-based — consider OCR."
        )

    # Check for syllabus-like keywords
    syllabus_keywords = [
        "grade", "assignment", "exam", "lecture", "credit", "office hours",
        "syllabus", "course", "homework", "midterm", "final", "week", "due"
    ]
    keyword_hits = sum(1 for kw in syllabus_keywords if kw.lower() in text.lower())

    if keyword_hits < 2:
        warnings.append(
            "Few syllabus-related keywords found. "
            "This may not be a course syllabus, or text extraction was poor."
        )

    # Assess quality
    if char_count < 200:
        quality = "poor"
        warnings.append("Very little text extracted — analysis may be incomplete.")
    elif char_count < 600 or keyword_hits < 3 or chars_per_page < 200:
        quality = "partial"
    else:
        quality = "good"

    return quality, warnings


def extract_with_pdfplumber(file_bytes: bytes) -> tuple[str, int]:
    """Primary extraction strategy: pdfplumber with layout analysis."""
    text_parts = []
    page_count = 0

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        page_count = len(pdf.pages)
        for page in pdf.pages:
            # Try standard text extraction
            text = page.extract_text(x_tolerance=3, y_tolerance=3)
            if text:
                text_parts.append(text)
            else:
                # Fallback: extract words individually
                words = page.extract_words()
                if words:
                    word_text = " ".join(w["text"] for w in words)
                    text_parts.append(word_text)

    return "\n\n".join(text_parts), page_count


def extract_with_pdfplumber_tables(file_bytes: bytes) -> tuple[str, int]:
    """
    Secondary strategy: also extract tables (grade breakdowns, schedules).
    Converts tables to readable text format.
    """
    text_parts = []
    page_count = 0

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        page_count = len(pdf.pages)
        for page in pdf.pages:
            # Normal text
            text = page.extract_text(x_tolerance=3, y_tolerance=3)
            if text:
                text_parts.append(text)

            # Tables → readable format
            tables = page.extract_tables()
            for table in tables:
                if not table:
                    continue
                table_lines = []
                for row in table:
                    if row:
                        clean_row = [cell.strip() if cell else "" for cell in row]
                        table_lines.append(" | ".join(clean_row))
                if table_lines:
                    text_parts.append("\n[TABLE]\n" + "\n".join(table_lines) + "\n[/TABLE]")

    return "\n\n".join(text_parts), page_count


def extract_pdf_text(file_bytes: bytes) -> ExtractionResult:
    """
    Main extraction function with multi-strategy fallback chain.

    Strategy order:
    1. pdfplumber with tables (best for syllabi with grade tables)
    2. pdfplumber standard (fallback if tables cause issues)
    3. Graceful degradation with meaningful error messages
    """
    warnings = []

    # ── STRATEGY 1: pdfplumber + tables ──
    try:
        text, page_count = extract_with_pdfplumber_tables(file_bytes)
        text = clean_extracted_text(text)
        quality, q_warnings = assess_text_quality(text, page_count)
        warnings.extend(q_warnings)

        if quality in ("good", "partial") and len(text.strip()) > 100:
            return ExtractionResult(
                text=text,
                page_count=page_count,
                char_count=len(text),
                method="pdfplumber+tables",
                quality=quality,
                warnings=warnings,
                is_usable=True
            )
    except Exception as e:
        warnings.append(f"pdfplumber+tables failed: {str(e)}")

    # ── STRATEGY 2: pdfplumber standard ──
    try:
        text, page_count = extract_with_pdfplumber(file_bytes)
        text = clean_extracted_text(text)
        quality, q_warnings = assess_text_quality(text, page_count)
        warnings.extend(q_warnings)

        if len(text.strip()) > 50:
            return ExtractionResult(
                text=text,
                page_count=page_count,
                char_count=len(text),
                method="pdfplumber_standard",
                quality=quality,
                warnings=warnings,
                is_usable=len(text.strip()) > 100
            )
    except Exception as e:
        warnings.append(f"pdfplumber standard failed: {str(e)}")

    # ── STRATEGY 3: Total failure ──
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            page_count = len(pdf.pages)
    except Exception:
        page_count = 0

    warnings.append(
        "All text extraction strategies failed. "
        "The PDF may be password-protected, corrupted, or purely image-based. "
        "Try exporting the syllabus to PDF from a Word document."
    )

    return ExtractionResult(
        text="",
        page_count=page_count,
        char_count=0,
        method="failed",
        quality="poor",
        warnings=warnings,
        is_usable=False
    )


def get_extraction_error_message(result: ExtractionResult) -> str:
    """
    Return a human-friendly error message for unusable PDFs.
    """
    if result.method == "failed":
        return (
            "Could not extract text from this PDF. "
            "It may be scanned, password-protected, or image-based. "
            "Try: File → Export as PDF from Word/Google Docs."
        )
    if result.quality == "poor":
        return (
            f"Extracted very little text ({result.char_count} characters from "
            f"{result.page_count} pages). "
            "The PDF may contain mostly images. "
            "Partial analysis will be attempted."
        )
    return "Unknown extraction issue."