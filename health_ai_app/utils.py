import re
from typing import Optional


def clean_text(text: str) -> str:
    """
    Basic normalization for extracted PDF text.
    """
    if not text:
        return ""
    # Normalize whitespace and common artifacts
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\r\n|\r", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def safe_float(value: Optional[str]) -> Optional[float]:
    """
    Parse a numeric string to float in a tolerant way.
    Returns None if parsing fails.
    """
    if value is None:
        return None
    try:
        cleaned = str(value).strip()
        cleaned = cleaned.replace(",", ".")
        number_match = re.search(r"-?\d+(?:\.\d+)?", cleaned)
        if not number_match:
            return None
        return float(number_match.group())
    except Exception:
        return None


def normalize_gender(raw: Optional[str]) -> Optional[str]:
    """
    Normalize gender labels to 'male' / 'female' where possible.
    """
    if not raw:
        return None
    text = raw.strip().lower()
    if text.startswith("m"):
        return "male"
    if text.startswith("f"):
        return "female"
    return None


def format_value(value: Optional[float], unit: Optional[str]) -> str:
    """
    Nicely format a value and its unit for display in the UI.
    """
    if value is None:
        return "Not found"
    if unit:
        return f"{value:.2f} {unit}"
    return f"{value:.2f}"


def summarize_status(status: Optional[str]) -> str:
    """
    Human-friendly label for low/normal/high classifications.
    """
    mapping = {
        "low": "Below reference range",
        "normal": "Within reference range",
        "high": "Above reference range",
    }
    if not status:
        return "Not classified"
    return mapping.get(status.lower(), status)

