from __future__ import annotations

import textwrap
from typing import Any, Dict, Optional

import streamlit as st

from .extraction import extract_report_data
from .interpretation import generate_lab_interpretation
from .navigation import generate_navigation_guidance
from .reference_ranges import get_lab_statuses
from .safety import check_red_flags
from .symptom_engine import analyze_symptoms
from .utils import format_value, summarize_status


PAGE_TITLE = "AI Health Report Interpretation Assistant"
DISCLAIMER_TEXT = (
    "This tool provides educational information only and does not replace professional "
    "medical advice, diagnosis, or treatment. It should not be used for emergencies."
)


def _build_explainability_items(
    lab_statuses: Dict[str, Dict[str, Optional[float]]],
    symptom_analysis: Dict[str, Optional[str]],
) -> Dict[str, Any]:
    abnormal_labs = []
    for name, payload in lab_statuses.items():
        status = payload.get("status")
        if status in ("low", "high"):
            value = payload.get("value")
            unit = payload.get("unit")
            ref_low = payload.get("ref_low")
            ref_high = payload.get("ref_high")
            ref_unit = payload.get("ref_unit") or unit
            descriptor = f"{name.upper()}: {format_value(value, unit)} — classified here as {status}"
            if ref_low is not None and ref_high is not None:
                descriptor += (
                    f" (approximate reference {ref_low:.1f}–{ref_high:.1f} {ref_unit})"
                )
            abnormal_labs.append(descriptor)

    matched_symptoms = symptom_analysis.get("matched_symptoms")
    symptom_summary = symptom_analysis.get("summary")

    reference_ranges_used = []
    for name, payload in lab_statuses.items():
        ref_low = payload.get("ref_low")
        ref_high = payload.get("ref_high")
        ref_unit = payload.get("ref_unit") or payload.get("unit")
        if ref_low is not None and ref_high is not None:
            reference_ranges_used.append(
                f"{name.upper()}: {ref_low:.1f}–{ref_high:.1f} {ref_unit}"
            )

    return {
        "abnormal_labs": abnormal_labs,
        "matched_symptoms": matched_symptoms,
        "symptom_summary": symptom_summary,
        "reference_ranges": reference_ranges_used,
    }


def main() -> None:
    st.set_page_config(page_title=PAGE_TITLE, layout="wide")

    st.title(PAGE_TITLE)
    st.caption(
        "Upload a PDF lab report to see a structured view of selected blood indices and "
        "cautious, educational explanations. This assistant does not provide diagnoses or "
        "treatment recommendations."
    )

    with st.expander("Read this first", expanded=True):
        st.write(DISCLAIMER_TEXT)

    st.markdown("---")

    # PDF Upload Section
    st.header("PDF Upload")
    uploaded_file = st.file_uploader(
        "Upload your lab report (PDF format)", type=["pdf"]
    )

    symptom_text = st.text_area(
        "Optional: Symptom description",
        help=(
            "You may describe any symptoms you are experiencing (for example, fatigue, "
            "shortness of breath, or other concerns). Do not include names or other "
            "personally identifying details."
        ),
    )

    if uploaded_file is None:
        st.info("Please upload a PDF lab report to begin.")
        st.markdown("---")
        st.markdown(f"**Disclaimer:** {DISCLAIMER_TEXT}")
        return

    # Extraction
    with st.spinner("Extracting information from the report..."):
        report = extract_report_data(uploaded_file)

    patient = report.get("patient", {})
    labs = report.get("labs", {})
    extraction_method = report.get("extraction_method", "none")

    # Extracted Values Display
    st.header("Extracted Values")
    col_demo, col_labs = st.columns([1, 2])
    with col_demo:
        st.subheader("Patient details (from report)")
        age = patient.get("age")
        gender = patient.get("gender")
        st.write(f"**Age:** {age if age is not None else 'Not found'}")
        st.write(f"**Gender:** {gender.capitalize() if gender else 'Not found'}")
        st.caption(f"Extraction method: {extraction_method}")

    lab_statuses = get_lab_statuses(labs, gender=patient.get("gender"))

    with col_labs:
        st.subheader("Key lab indices")
        table_rows = []
        for name, payload in lab_statuses.items():
            value = payload.get("value")
            unit = payload.get("unit")
            status = payload.get("status")
            ref_low = payload.get("ref_low")
            ref_high = payload.get("ref_high")
            ref_unit = payload.get("ref_unit") or unit

            ref_str = ""
            if ref_low is not None and ref_high is not None:
                ref_str = f"{ref_low:.1f}–{ref_high:.1f} {ref_unit}"

            table_rows.append(
                {
                    "Test": name.upper(),
                    "Value": format_value(value, unit),
                    "Status": summarize_status(status),
                    "Reference range": ref_str or "Not available",
                }
            )

        st.table(table_rows)

    # Safety and symptom processing
    safety_result = check_red_flags(symptom_text or "")
    symptom_analysis = analyze_symptoms(symptom_text or "", lab_statuses)

    # Interpretation Section
    st.header("Interpretation (educational only)")
    interpretation = generate_lab_interpretation(
        lab_statuses,
        gender=patient.get("gender"),
        age=patient.get("age"),
    )

    for para in interpretation.get("overview", []):
        st.write(para)

    if safety_result.get("has_red_flags"):
        urgent_message = safety_result.get("urgent_message") or ""
        st.error(urgent_message)
        st.info(
            "Because of the potential urgency of these symptoms, the additional comments "
            "below should be treated as general background information only."
        )

    for msg in interpretation.get("details", []):
        st.markdown(f"- {msg}")

    for note in interpretation.get("safety_note", []):
        st.warning(note)

    # Symptom Correlation Output
    st.header("Symptom Correlation (rule-based)")
    if symptom_text.strip():
        st.write(symptom_analysis.get("summary"))
        relevance = symptom_analysis.get("relevance")
        if relevance:
            st.write(f"**Relevance level (qualitative):** {relevance}")
        matched_symptoms = symptom_analysis.get("matched_symptoms")
        if matched_symptoms:
            st.caption(f"Keywords detected: {matched_symptoms}")
    else:
        st.info("No symptoms were entered, so no symptom correlation could be performed.")

    # Care Navigation Section
    st.header("Care Navigation Guidance")
    nav_lines = generate_navigation_guidance(
        lab_statuses=lab_statuses,
        symptom_summary=symptom_analysis.get("summary"),
        safety_result=safety_result,
    )
    for line in nav_lines:
        st.write(line)

    # Explainability Section
    st.header("Explainability")
    st.caption("Why this guidance was generated.")
    explain = _build_explainability_items(lab_statuses, symptom_analysis)

    st.subheader("Abnormal lab values considered")
    if explain["abnormal_labs"]:
        for item in explain["abnormal_labs"]:
            st.markdown(f"- {item}")
    else:
        st.markdown("- No clearly abnormal values were identified based on the reference ranges used here.")

    st.subheader("Matched symptoms")
    if explain["matched_symptoms"]:
        st.markdown(f"- {explain['matched_symptoms']}")
    else:
        st.markdown("- No specific symptom keywords matched the current rule set.")

    st.subheader("Reference ranges used")
    if explain["reference_ranges"]:
        for item in explain["reference_ranges"]:
            st.markdown(f"- {item}")
    else:
        st.markdown("- No reference ranges were available for the extracted values.")

    # Disclaimer Footer
    st.markdown("---")
    st.markdown(
        textwrap.dedent(
            """
            **Important disclaimer**

            This tool provides educational information only and does not replace professional medical advice, diagnosis, or treatment. 
            It cannot assess emergencies. Always speak with a qualified healthcare professional about your health and your lab results, 
            and seek urgent in-person care or contact local emergency services if you think you may be experiencing a medical emergency.
            """
        )
    )


if __name__ == "__main__":
    main()

