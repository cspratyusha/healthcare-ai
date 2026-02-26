from __future__ import annotations

import io
import re
from typing import Any, Dict, Optional

import pdfplumber
from PIL import Image

try:
    import pytesseract
except Exception:  # pragma: no cover - pytesseract might not be installed at runtime
    pytesseract = None  # type: ignore

try:  # pragma: no cover - depends on execution context
    from .utils import clean_text, safe_float, normalize_gender  # type: ignore
except ImportError:
    from utils import clean_text, safe_float, normalize_gender


HEMOGLOBIN_PATTERN = re.compile(
    r"hemoglobin(?:\s*[:\-]|\s+)\s*"
    r"(-?\d+(?:[.,]\d+)?)\s*"
    r"(g\/?dL|g per dL|g\s*\/\s*dL)?",
    re.IGNORECASE,
)

MCV_PATTERN = re.compile(
    r"\bMCV\b(?:\s*[:\-]|\s+)\s*"
    r"(-?\d+(?:[.,]\d+)?)\s*"
    r"(fL)?",
    re.IGNORECASE,
)

MCH_PATTERN = re.compile(
    r"\bMCH\b(?:\s*[:\-]|\s+)\s*"
    r"(-?\d+(?:[.,]\d+)?)\s*"
    r"(pg)?",
    re.IGNORECASE,
)

MCHC_PATTERN = re.compile(
    r"\bMCHC\b(?:\s*[:\-]|\s+)\s*"
    r"(-?\d+(?:[.,]\d+)?)\s*"
    r"(g\/?dL|g per dL|g\s*\/\s*dL)?",
    re.IGNORECASE,
)

GENDER_PATTERN = re.compile(
    r"(?:gender|sex)\s*[:\-]?\s*(male|female)",
    re.IGNORECASE,
)

AGE_PATTERN = re.compile(
    r"\bage\b\s*[:\-]?\s*(\d{1,3})",
    re.IGNORECASE,
)


def _extract_text_pdfplumber(file_like: Any) -> str:
    """
    Extract text from a PDF using pdfplumber.
    """
    file_like.seek(0)
    text_chunks = []
    with pdfplumber.open(file_like) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text() or ""
            text_chunks.append(extracted)
    return clean_text("\n".join(text_chunks))


def _extract_text_ocr(file_like: Any) -> str:
    """
    Fallback OCR extraction using pytesseract on page images.
    """
    if pytesseract is None:
        return ""

    file_like.seek(0)
    ocr_chunks = []
    try:
        with pdfplumber.open(file_like) as pdf:
            for page in pdf.pages:
                try:
                    page_image = page.to_image(resolution=300)
                    pil_image: Image.Image = page_image.original
                    ocr_text = pytesseract.image_to_string(pil_image)
                    ocr_chunks.append(ocr_text or "")
                except Exception:
                    # If a single page fails OCR, continue with the rest
                    continue
    except Exception:
        return ""
    return clean_text("\n".join(ocr_chunks))


def _parse_gender(text: str) -> Optional[str]:
    match = GENDER_PATTERN.search(text)
    if match:
        return normalize_gender(match.group(1))

    # Fallback heuristic: look for standalone "Male" or "Female"
    generic_match = re.search(r"\b(male|female)\b", text, re.IGNORECASE)
    if generic_match:
        return normalize_gender(generic_match.group(1))
    return None


def _parse_age(text: str) -> Optional[int]:
    match = AGE_PATTERN.search(text)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            return None
    return None


def _parse_analyte(
    pattern: re.Pattern, text: str, default_unit: Optional[str] = None
) -> Dict[str, Optional[Any]]:
    match = pattern.search(text)
    if not match:
        return {"value": None, "unit": default_unit}
    value = safe_float(match.group(1))
    unit = match.group(2) or default_unit
    if unit:
        unit = unit.replace(" ", "").replace("per", "/").replace("dL", "dL")
        unit = unit.replace("g/dL", "g/dL")
    return {"value": value, "unit": unit or default_unit}


def extract_report_data(uploaded_file: Any) -> Dict[str, Any]:
    """
    High-level helper used by the Streamlit app.

    Accepts a Streamlit UploadedFile or any file-like object.
    Returns:
        {
          "patient": {"age": int | None, "gender": str | None},
          "labs": {
              "hemoglobin": {"value": float | None, "unit": "g/dL"},
              "mcv": {"value": float | None, "unit": "fL"},
              "mch": {"value": float | None, "unit": "pg"},
              "mchc": {"value": float | None, "unit": "g/dL"},
          },
          "raw_text": "...",
          "extraction_method": "pdfplumber" | "ocr" | "none",
        }
    """
    # Streamlit's UploadedFile can be passed directly; for other inputs, wrap in BytesIO
    if hasattr(uploaded_file, "read"):
        # Make a private copy so we can seek safely
        file_bytes = uploaded_file.read()
        file_like: Any = io.BytesIO(file_bytes)
    else:
        file_like = io.BytesIO(uploaded_file)

    text = ""
    method = "none"

    try:
        text = _extract_text_pdfplumber(file_like)
        method = "pdfplumber"
    except Exception:
        text = ""
        method = "none"

    # If pdfplumber extraction is empty or extremely short, try OCR
    if len(text) < 40:
        ocr_text = _extract_text_ocr(file_like)
        if len(ocr_text) > len(text):
            text = ocr_text
            method = "ocr"

    text = clean_text(text)

    gender = _parse_gender(text)
    age = _parse_age(text)

    hemoglobin = _parse_analyte(HEMOGLOBIN_PATTERN, text, default_unit="g/dL")
    mcv = _parse_analyte(MCV_PATTERN, text, default_unit="fL")
    mch = _parse_analyte(MCH_PATTERN, text, default_unit="pg")
    mchc = _parse_analyte(MCHC_PATTERN, text, default_unit="g/dL")

    return {
        "patient": {
            "age": age,
            "gender": gender,
        },
        "labs": {
            "hemoglobin": hemoglobin,
            "mcv": mcv,
            "mch": mch,
            "mchc": mchc,
        },
        "raw_text": text,
        "extraction_method": method,
    }

