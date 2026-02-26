## AI Health Report Interpretation Assistant

This folder contains a Streamlit-based prototype for a **Health Report Interpretation Assistant** focused on selected anemia-related indices.  
It is designed for hackathon/demo use and provides **educational, non-diagnostic** explanations.

### Features

- PDF upload of lab reports (PDF)
- Text extraction with **pdfplumber** and OCR fallback using **pytesseract** (via Pillow)
- Parsing of:
  - Hemoglobin
  - MCV
  - MCH
  - MCHC
  - Age
  - Gender
- Reference-range comparison and cautious interpretation text
- Optional free-text symptom input and rule-based correlation
- Red-flag safety layer that surfaces urgent-care messaging
- Care navigation guidance and explainability section
- Strong disclaimer and cautious language throughout

### Project structure (inside `health_ai_app/`)

- `streamlit_app.py` – main Streamlit UI entrypoint
- `extraction.py` – PDF and OCR extraction + parsing into structured values
- `reference_ranges.py` – reference ranges and classification logic
- `interpretation.py` – rule-based, cautious interpretation text
- `symptom_engine.py` – symptom correlation rules
- `navigation.py` – care navigation guidance
- `safety.py` – red-flag safety checks
- `utils.py` – shared helpers (formatting, parsing)

### Dependencies

Core Python packages (expected to be in the root `requirements.txt`):

- `streamlit`
- `pdfplumber`
- `pytesseract`
- `Pillow`
- `regex` or built-in `re`

Make sure the root `requirements.txt` includes at least:

```text
streamlit
pdfplumber
pytesseract
Pillow
regex
```

Then install:

```bash
pip install -r requirements.txt
```

### Tesseract OCR installation

`pytesseract` is a Python wrapper around the Tesseract executable, which must be installed separately:

- **Windows**: Install Tesseract (for example, from the official project or a trusted binary distribution) and ensure the `tesseract.exe` directory is added to your `PATH`.
- If needed, you can configure the executable path manually in your code by setting:

```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\\Path\\to\\tesseract.exe"
```

The app will still run if OCR is not available, but extraction quality on scanned/image-based PDFs will be reduced.

### How to run

From the project root (where `health_ai_app/` lives), run:

```bash
streamlit run health_ai_app/streamlit_app.py
```

Then open the URL shown in the terminal (typically `http://localhost:8501`) in your browser.

### Safety and limitations

- This assistant **does not** provide diagnoses or treatment recommendations.
- It uses simple, rule-based logic and reference ranges only.
- Lab reports can vary widely in layout and format; extraction may fail or miss values.
- All outputs should be considered **educational** and must be reviewed with a licensed healthcare professional.

