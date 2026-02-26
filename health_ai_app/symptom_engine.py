from __future__ import annotations

from typing import Dict, List, Optional


FATIGUE_KEYWORDS = [
    "fatigue",
    "tired",
    "tiredness",
    "exhausted",
    "exhaustion",
    "weak",
    "weakness",
    "low energy",
]


def analyze_symptoms(
    symptom_text: str,
    lab_statuses: Dict[str, Dict[str, Optional[float]]],
) -> Dict[str, Optional[str]]:
    """
    Rule-based symptom correlation.

    Currently implemented:
      - If hemoglobin is low AND fatigue-like symptom terms are present:
        * describe the combination
        * assign a qualitative relevance level
    """
    if not symptom_text:
        return {
            "summary": None,
            "relevance": None,
            "matched_symptoms": None,
        }

    text = symptom_text.lower()
    matched_symptoms: List[str] = [
        kw for kw in FATIGUE_KEYWORDS if kw in text
    ]

    hemoglobin_info = lab_statuses.get("hemoglobin", {})
    hemo_status = hemoglobin_info.get("status")
    hemo_value = hemoglobin_info.get("value")  # type: ignore[assignment]

    if hemo_status == "low" and matched_symptoms:
        # Basic heuristic: more pronounced drop in hemoglobin -> higher qualitative relevance
        relevance = "Moderate"
        if hemo_value is not None and hemo_value < 8:
            relevance = "High"

        summary = (
            "The combination of a hemoglobin value classified here as below the usual "
            "reference range and reported fatigue-like symptoms may be relevant. "
            "This does not indicate a diagnosis. Only a healthcare professional can "
            "assess how these findings relate to your overall health."
        )

        return {
            "summary": summary,
            "relevance": relevance,
            "matched_symptoms": ", ".join(sorted(set(matched_symptoms))),
        }

    # No strong rule triggered
    if matched_symptoms:
        return {
            "summary": (
                "Some symptoms you described, such as fatigue or low energy, are sometimes "
                "mentioned in relation to blood count changes. This tool cannot determine "
                "whether your symptoms are related to your lab values. A clinician can review "
                "both together for you."
            ),
            "relevance": "Low",
            "matched_symptoms": ", ".join(sorted(set(matched_symptoms))),
        }

    return {
        "summary": (
            "No specific rule-based links between the symptoms described and the extracted "
            "lab values were identified. This does not rule out any condition. Any persistent "
            "or concerning symptoms should be discussed with a healthcare professional."
        ),
        "relevance": "Low",
        "matched_symptoms": None,
    }

