from __future__ import annotations

from typing import Dict, Optional, Tuple


HEMOGLOBIN_RANGES = {
    "male": (13.0, 17.0),   # g/dL
    "female": (12.0, 15.0),  # g/dL
}

MCV_RANGE = (80.0, 100.0)   # fL
MCH_RANGE = (27.0, 33.0)    # pg
MCHC_RANGE = (32.0, 36.0)   # g/dL


def get_range(
    analyte: str, gender: Optional[str] = None
) -> Optional[Tuple[float, float, str]]:
    """
    Return (low, high, unit) for a given analyte.
    """
    key = analyte.lower()
    if key == "hemoglobin":
        unit = "g/dL"
        if gender:
            gender_key = gender.lower()
            if gender_key in HEMOGLOBIN_RANGES:
                low, high = HEMOGLOBIN_RANGES[gender_key]
                return low, high, unit
        # Generic range if gender not available
        return 12.0, 17.0, unit

    if key == "mcv":
        return MCV_RANGE[0], MCV_RANGE[1], "fL"
    if key == "mch":
        return MCH_RANGE[0], MCH_RANGE[1], "pg"
    if key == "mchc":
        return MCHC_RANGE[0], MCHC_RANGE[1], "g/dL"
    return None


def classify_value(
    analyte: str, value: Optional[float], gender: Optional[str] = None
) -> Optional[str]:
    """
    Classify a lab value as 'low', 'normal', or 'high' based on reference ranges.
    """
    if value is None:
        return None
    range_info = get_range(analyte, gender)
    if not range_info:
        return None
    low, high, _ = range_info
    if value < low:
        return "low"
    if value > high:
        return "high"
    return "normal"


def get_lab_statuses(
    labs: Dict[str, Dict[str, Optional[float]]],
    gender: Optional[str],
) -> Dict[str, Dict[str, Optional[float]]]:
    """
    Build a structured view with value, unit, classification, and reference range.
    """
    statuses: Dict[str, Dict[str, Optional[float]]] = {}
    for analyte, payload in labs.items():
        value = payload.get("value") if payload else None  # type: ignore[assignment]
        unit = payload.get("unit") if payload else None  # type: ignore[assignment]
        status = classify_value(analyte, value, gender)
        ref_range = get_range(analyte, gender)
        if ref_range:
            low, high, ref_unit = ref_range
        else:
            low = high = None
            ref_unit = unit

        statuses[analyte] = {
            "value": value,
            "unit": unit,
            "status": status,
            "ref_low": low,
            "ref_high": high,
            "ref_unit": ref_unit,
        }
    return statuses

