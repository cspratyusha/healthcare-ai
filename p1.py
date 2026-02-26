import pandas as pd
import os
import random
from faker import Faker
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

# Load dataset
data = pd.read_csv("anemia.csv")

# Create output folder
os.makedirs("synthetic_anemia_reports", exist_ok=True)

fake = Faker()
styles = getSampleStyleSheet()

for index, row in data.iterrows():

    # Convert gender
    gender = "Male" if row["Gender"] == 0 else "Female"

    # Convert result
    anemia_status = "Anemic" if row["Result"] == 1 else "Normal"

    # Generate fake patient details
    patient_name = fake.name()
    age = random.randint(18, 70)
    report_id = f"RPT{random.randint(10000,99999)}"

    filename = f"synthetic_anemia_reports/Anemia_Report_{index}.pdf"
    doc = SimpleDocTemplate(filename)
    elements = []

    # Hospital Header
    elements.append(Paragraph("<b>Global Diagnostic Laboratory</b>", styles["Title"]))
    elements.append(Spacer(1, 0.3 * inch))

    # Patient Details
    elements.append(Paragraph(f"Report ID: {report_id}", styles["Normal"]))
    elements.append(Paragraph(f"Patient Name: {patient_name}", styles["Normal"]))
    elements.append(Paragraph(f"Age: {age}", styles["Normal"]))
    elements.append(Paragraph(f"Gender: {gender}", styles["Normal"]))
    elements.append(Spacer(1, 0.3 * inch))

    # CBC Table
    table_data = [
        ["Test", "Result", "Unit", "Reference Range"],
        ["Hemoglobin", row["Hemoglobin"], "g/dL", "12-16"],
        ["MCV", row["MCV"], "fL", "80-100"],
        ["MCH", row["MCH"], "pg", "27-33"],
        ["MCHC", row["MCHC"], "g/dL", "32-36"],
    ]

    table = Table(table_data)
    table.setStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
    ])

    elements.append(table)
    elements.append(Spacer(1, 0.4 * inch))

    # Add interpretation section
    elements.append(Paragraph("<b>Clinical Interpretation:</b>", styles["Heading2"]))
    elements.append(Spacer(1, 0.1 * inch))

    if anemia_status == "Anemic":
        elements.append(Paragraph(
            "Findings suggest anemia. Clinical correlation recommended.",
            styles["Normal"]
        ))
    else:
        elements.append(Paragraph(
            "All hematological parameters are within normal range.",
            styles["Normal"]
        ))

    doc.build(elements)

print("All synthetic anemia reports generated successfully!")