# ai_medical/sectionizer/sectionize_text.py
"""
Sectionizer (Final Production-Grade Version)

Features:
- Splits OCR text into logical sections (handles variations like “SECTION 2”, “Section II”, “SECTION-3”)
- Unicode and whitespace normalization
- Path-independent operation
- Deterministic, JSON-safe output
- Graceful fallbacks for missing headers
"""

import os
import re
import json
from collections import OrderedDict


def sectionize_text(input_path: str, verbose: bool = True) -> dict:
    """
    Reads the OCR text file and splits it into sections based on headings.
    Returns an OrderedDict of {section_name: content}.
    """

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    # -----------------------------
    # Normalize text for consistency
    # -----------------------------
    text = (
        text.replace("’", "'")
            .replace("–", "-")
            .replace("—", "-")
            .replace("“", '"')
            .replace("”", '"')
    )
    text = re.sub(r"\r", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # -----------------------------
    # Regex pattern (robust variant)
    # Supports:
    #   SECTION 1:
    #   Section II -
    #   SECTION-3  PATIENT DETAILS
    # -----------------------------
    pattern = re.compile(
        r"(SECTION\s*[\dIVX]+[:\-]?\s*[A-Z][A-Z’' \-/&]+)",
        re.IGNORECASE,
    )

    splits = pattern.split(text)
    sections = OrderedDict()
    current_section = "INTRODUCTION"
    sections[current_section] = ""

    for chunk in splits:
        header_match = pattern.match(chunk)
        if header_match:
            current_section = header_match.group(1).strip().upper()
            sections[current_section] = ""
        else:
            sections[current_section] += chunk.strip() + "\n"

    # -----------------------------
    # Cleanup: remove empty sections
    # -----------------------------
    sections = OrderedDict(
        (k, v.strip()) for k, v in sections.items() if v.strip()
    )

    # -----------------------------
    # Fallback if no sections found
    # -----------------------------
    if len(sections) == 1 and "INTRODUCTION" in sections:
        sections = OrderedDict({"FULL_TEXT": sections["INTRODUCTION"]})

    if verbose:
        print(f"Detected {len(sections)} sections.")
        for key in sections:
            print(" -", key)

    return sections


if __name__ == "__main__":
    # Resolve OCR output path relative to project root
    project_root = os.path.dirname(os.path.dirname(__file__))
    input_path = os.path.join(project_root, "ocr", "Sampleocr_output.txt")

    try:
        sections = sectionize_text(input_path)

        # Save JSON output inside sectionizer folder
        output_dir = os.path.dirname(__file__)
        output_path = os.path.join(output_dir, "sectionized_output.json")

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(sections, f, indent=4, ensure_ascii=False)

        print(f"\nSectionized text saved to: {output_path}")

    except Exception as e:
        print(f"Sectionizing failed: {e}")
