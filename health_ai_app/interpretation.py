from __future__ import annotations

from typing import Dict, List, Optional


def _lab_sentence(
    name: str,
    status: Optional[str],
    value: Optional[float],
    unit: Optional[str],
    ref_low: Optional[float],
    ref_high: Optional[float],
    ref_unit: Optional[str],
) -> Optional[str]:
    if status is None or value is None:
        return None

    pretty_name = name.upper()
    unit_display = unit or ref_unit or ""
    value_str = f"{value:.2f} {unit_display}".strip()

    ref_str = ""
    if ref_low is not None and ref_high is not None:
        ref_unit_display = ref_unit or unit_display
        ref_str = f" (typical reference range approximately {ref_low:.1f}–{ref_high:.1f} {ref_unit_display})"

    if status == "low":
        return (
            f"Your {pretty_name} value is below the typical reference range at {value_str}.{ref_str} "
            f"Lower {pretty_name} levels can sometimes be associated with certain health conditions, "
            f"such as anemia in the case of hemoglobin. This information is educational and does not "
            f"confirm any diagnosis. A healthcare professional can review this result in the context of "
            f"your overall health."
        )
    if status == "high":
        return (
            f"Your {pretty_name} value is above the typical reference range at {value_str}.{ref_str} "
            f"Higher {pretty_name} levels may occasionally be seen in some medical situations. This tool "
            f"cannot determine the cause or provide a diagnosis. Discussing this value with a qualified "
            f"healthcare professional can help put it into proper context."
        )
    if status == "normal":
        return (
            f"Your {pretty_name} value of {value_str}{ref_str} falls within the usual "
            f"reference range reported here. While this can be reassuring, only a healthcare professional "
            f"can interpret lab results alongside your symptoms and medical history."
        )
    return None


def generate_lab_interpretation(
    lab_statuses: Dict[str, Dict[str, Optional[float]]],
    gender: Optional[str],
    age: Optional[int],
) -> Dict[str, List[str]]:
    """
    Create cautious, educational text about the lab values.
    """
    messages: List[str] = []
    overview: List[str] = []

    if gender or age is not None:
        demographics = []
        if age is not None:
            demographics.append(f"age {age}")
        if gender:
            demographics.append(gender.lower())
        if demographics:
            overview.append(
                "The following comments are based on values reported in your lab document "
                f"and general reference ranges, considering the information available ("
                + ", ".join(demographics)
                + ")."
            )

    any_value_found = any(
        payload.get("value") is not None for payload in lab_statuses.values()
    )
    if not any_value_found:
        overview.append(
            "This tool was not able to confidently locate the target lab values in the uploaded report. "
            "Formatting differences or image-based PDFs can limit automated extraction. "
            "You may wish to review the report directly or provide it to a healthcare professional."
        )

    for name, payload in lab_statuses.items():
        msg = _lab_sentence(
            name=name,
            status=payload.get("status"),
            value=payload.get("value"),  # type: ignore[arg-type]
            unit=payload.get("unit"),
            ref_low=payload.get("ref_low"),  # type: ignore[arg-type]
            ref_high=payload.get("ref_high"),  # type: ignore[arg-type]
            ref_unit=payload.get("ref_unit"),
        )
        if msg:
            messages.append(msg)

    if not messages and any_value_found:
        messages.append(
            "The values detected appear to fall within the reference ranges provided in the report. "
            "Only a licensed healthcare professional can confirm whether these results are appropriate "
            "for you personally."
        )

    safety_note = (
        "This assistant does not provide diagnoses, treatment decisions, or a substitute for in-person "
        "clinical assessment. Any concerns about your health or your lab results should be discussed "
        "with a qualified healthcare professional."
    )

    return {
        "overview": overview,
        "details": messages,
        "safety_note": [safety_note],
    }

