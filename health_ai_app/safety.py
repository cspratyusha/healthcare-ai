from __future__ import annotations

from typing import Dict, List


RED_FLAG_PHRASES = {
    "chest pain": ["chest pain", "pressure in chest", "tight chest"],
    "fainting": ["fainting", "passed out", "loss of consciousness", "blackout"],
    "severe shortness of breath": [
        "severe shortness of breath",
        "struggling to breathe",
        "cannot catch my breath",
        "difficulty breathing",
    ],
    "uncontrolled bleeding": [
        "uncontrolled bleeding",
        "bleeding that will not stop",
        "very heavy bleeding",
    ],
}


def check_red_flags(symptom_text: str) -> Dict[str, object]:
    """
    Look for simple keyword-based red flags that should trigger an urgent care message.
    """
    text = (symptom_text or "").lower()
    matched: List[str] = []

    for label, phrases in RED_FLAG_PHRASES.items():
        for phrase in phrases:
            if phrase in text:
                matched.append(label)
                break

    has_red_flags = len(matched) > 0

    urgent_message = None
    if has_red_flags:
        unique = ", ".join(sorted(set(matched)))
        urgent_message = (
            "Some of the symptoms you described (for example: "
            f"{unique}) can sometimes be associated with medical emergencies. "
            "This tool cannot assess emergencies or provide real-time clinical triage. "
            "If you are experiencing these symptoms now, please seek urgent in-person medical care "
            "or contact your local emergency services immediately."
        )

    return {
        "has_red_flags": has_red_flags,
        "matched_labels": sorted(set(matched)),
        "urgent_message": urgent_message,
    }

