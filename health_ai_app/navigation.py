from __future__ import annotations

from typing import Dict, List, Optional


def _any_abnormal(lab_statuses: Dict[str, Dict[str, Optional[float]]]) -> bool:
    for payload in lab_statuses.values():
        if payload.get("status") in ("low", "high"):
            return True
    return False


def generate_navigation_guidance(
    lab_statuses: Dict[str, Dict[str, Optional[float]]],
    symptom_summary: Optional[str],
    safety_result: Dict[str, object],
) -> List[str]:
    """
    Provide high-level, non-diagnostic care navigation guidance.
    """
    lines: List[str] = []

    lines.append(
        "A good first step for most questions about lab results is to speak with a "
        "general physician or primary care clinician. They can review your full report, "
        "your symptoms, and your medical history."
    )

    if _any_abnormal(lab_statuses):
        lines.append(
            "Because at least one value here is shown as outside the usual reference "
            "range, it may be reasonable to schedule a non-urgent appointment with a "
            "general physician to discuss these results."
        )

    if safety_result.get("has_red_flags"):
        lines.append(
            "Some of the symptoms described may require urgent attention. In such "
            "situations, emergency or urgent-care services are more appropriate than "
            "routine appointments or online tools."
        )

    if symptom_summary:
        lines.append(
            "Bringing a brief written summary of your main symptoms, when they started, "
            "and what makes them better or worse can help your clinician understand your "
            "situation more clearly."
        )

    lines.append(
        "You may consider asking your doctor questions such as:\n"
        "- \"How do these lab results fit with my symptoms and overall health?\"\n"
        "- \"Are there any additional tests or follow-up you would recommend?\"\n"
        "- \"Is there anything I can monitor at home while we follow up on these results?\""
    )

    return lines

