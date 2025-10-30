from fpdf import FPDF

# Create instance of FPDF class
pdf = FPDF()

# Add a page
pdf.add_page()

# Set title with a Unicode-compatible font (using Arial Unicode MS)
pdf.add_font('ArialUnicode', '', '/Library/Fonts/Arial Unicode.ttf', uni=True)
pdf.set_font('ArialUnicode', '', 16)
pdf.cell(200, 10, txt="CITY GENERAL HOSPITAL", ln=True, align="C")
pdf.cell(200, 10, txt="Medical Record", ln=True, align="C")

# Add patient information
pdf.ln(10)
pdf.set_font("ArialUnicode", size=12)
pdf.cell(200, 10, txt="Patient Information:", ln=True)
pdf.cell(200, 10, txt="Name: John Smith", ln=True)
pdf.cell(200, 10, txt="Date of Birth: 03/15/1975", ln=True)
pdf.cell(200, 10, txt="Medical Record Number: MRN-2024-001234", ln=True)
pdf.cell(200, 10, txt="Date of Visit: October 20, 2024", ln=True)

# Chief Complaint
pdf.ln(10)
pdf.cell(200, 10, txt="Chief Complaint:", ln=True)
pdf.multi_cell(0, 10, txt="Patient presents with complaints of increased thirst, frequent urination, and fatigue over the past 3 months.")

# Vital Signs
pdf.ln(10)
pdf.cell(200, 10, txt="Vital Signs:", ln=True)
pdf.cell(200, 10, txt="Blood Pressure: 145/92 mmHg", ln=True)
pdf.cell(200, 10, txt="Heart Rate: 78 bpm", ln=True)
pdf.cell(200, 10, txt="BMI: 30.1", ln=True)

# Medical History
pdf.ln(10)
pdf.cell(200, 10, txt="Medical History:", ln=True)
pdf.multi_cell(0, 10, txt="• Type 2 Diabetes Mellitus (diagnosed 2020)\n• Hypertension (diagnosed 2018)\n• Hyperlipidemia")

# Current Medications
pdf.ln(10)
pdf.cell(200, 10, txt="Current Medications:", ln=True)
pdf.multi_cell(0, 10, txt="1. Metformin 1000mg - twice daily\n2. Lisinopril 20mg - once daily\n3. Atorvastatin 40mg - once daily at bedtime\n4. Aspirin 81mg - once daily")

# Laboratory Results
pdf.ln(10)
pdf.cell(200, 10, txt="Laboratory Results:", ln=True)
pdf.cell(200, 10, txt="Test                  Result           Reference", ln=True)
pdf.cell(200, 10, txt="Fasting Blood Glucose   165 mg/dL     70-100 mg/dL", ln=True)
pdf.cell(200, 10, txt="HbA1c                 8.2%           <5.7%", ln=True)
pdf.cell(200, 10, txt="Total Cholesterol      220 mg/dL     <200 mg/dL", ln=True)
pdf.cell(200, 10, txt="Creatinine             1.1 mg/dL     0.7-1.3 mg/dL", ln=True)

# Assessment
pdf.ln(10)
pdf.cell(200, 10, txt="Assessment:", ln=True)
pdf.multi_cell(0, 10, txt="1. Type 2 Diabetes Mellitus - poorly controlled\n2. Essential Hypertension - moderately controlled\n3. Hyperlipidemia - on treatment")

# Signature
pdf.ln(10)
pdf.cell(200, 10, txt="Dr. Sarah Johnson, MD", ln=True)
pdf.cell(200, 10, txt="Internal Medicine", ln=True)
pdf.cell(200, 10, txt="Date: October 20, 2024", ln=True)

# Save PDF to a file
pdf_output_path = "/Users/thanhle/Library/CloudStorage/GoogleDrive-lenhothanh.nsl@gmail.com/.shortcut-targets-by-id/1Je2GU6cAmriwQ_9lhORCt8JeHBjH-2Yq/ELEC5620/Code/5620medai/web_app/UC1_models/sample_medical_document_detailed_with_unicode.pdf"
pdf.output(pdf_output_path)

print(f"PDF saved to: {pdf_output_path}")
