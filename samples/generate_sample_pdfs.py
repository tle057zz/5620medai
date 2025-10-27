#!/usr/bin/env python3
"""
Generate Sample Medical PDFs for Testing
Creates PDF versions of text-based medical documents for testing the document upload feature
"""

import os
from datetime import datetime

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("⚠️  ReportLab not installed. Install with: pip install reportlab")
    print("Falling back to text file generation only.")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def create_medical_report_pdf():
    """Create sample medical report PDF"""
    if not REPORTLAB_AVAILABLE:
        print("❌ Cannot create PDF - ReportLab not available")
        return
    
    filename = os.path.join(SCRIPT_DIR, "sample_medical_report_1.pdf")
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#0066cc'))
    story.append(Paragraph("CITY GENERAL HOSPITAL", title_style))
    story.append(Paragraph("Medical Record", styles['Heading2']))
    story.append(Spacer(1, 0.2*inch))
    
    # Patient Info
    story.append(Paragraph("<b>Patient Information:</b>", styles['Heading3']))
    patient_data = [
        ["Name:", "John Smith"],
        ["Date of Birth:", "03/15/1975"],
        ["Medical Record Number:", "MRN-2024-001234"],
        ["Date of Visit:", "October 20, 2024"]
    ]
    t = Table(patient_data, colWidths=[2*inch, 4*inch])
    t.setStyle(TableStyle([('FONTSIZE', (0, 0), (-1, -1), 10)]))
    story.append(t)
    story.append(Spacer(1, 0.2*inch))
    
    # Chief Complaint
    story.append(Paragraph("<b>Chief Complaint:</b>", styles['Heading3']))
    story.append(Paragraph("Patient presents with complaints of increased thirst, frequent urination, and fatigue over the past 3 months.", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Vital Signs
    story.append(Paragraph("<b>Vital Signs:</b>", styles['Heading3']))
    vitals_data = [
        ["Blood Pressure:", "145/92 mmHg"],
        ["Heart Rate:", "78 bpm"],
        ["BMI:", "30.1"]
    ]
    t = Table(vitals_data, colWidths=[2*inch, 2*inch])
    story.append(t)
    story.append(Spacer(1, 0.2*inch))
    
    # Medical History
    story.append(Paragraph("<b>Medical History:</b>", styles['Heading3']))
    story.append(Paragraph("• Type 2 Diabetes Mellitus (diagnosed 2020)", styles['Normal']))
    story.append(Paragraph("• Hypertension (diagnosed 2018)", styles['Normal']))
    story.append(Paragraph("• Hyperlipidemia", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Current Medications
    story.append(Paragraph("<b>Current Medications:</b>", styles['Heading3']))
    story.append(Paragraph("1. Metformin 1000mg - twice daily", styles['Normal']))
    story.append(Paragraph("2. Lisinopril 20mg - once daily", styles['Normal']))
    story.append(Paragraph("3. Atorvastatin 40mg - once daily at bedtime", styles['Normal']))
    story.append(Paragraph("4. Aspirin 81mg - once daily", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Lab Results
    story.append(Paragraph("<b>Laboratory Results:</b>", styles['Heading3']))
    lab_data = [
        ["Test", "Result", "Reference"],
        ["Fasting Blood Glucose", "165 mg/dL", "70-100 mg/dL"],
        ["HbA1c", "8.2%", "<5.7%"],
        ["Total Cholesterol", "220 mg/dL", "<200 mg/dL"],
        ["Creatinine", "1.1 mg/dL", "0.7-1.3 mg/dL"]
    ]
    t = Table(lab_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(t)
    story.append(Spacer(1, 0.2*inch))
    
    # Assessment
    story.append(Paragraph("<b>Assessment:</b>", styles['Heading3']))
    story.append(Paragraph("1. Type 2 Diabetes Mellitus - poorly controlled", styles['Normal']))
    story.append(Paragraph("2. Essential Hypertension - moderately controlled", styles['Normal']))
    story.append(Paragraph("3. Hyperlipidemia - on treatment", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Signature
    story.append(Paragraph("Dr. Sarah Johnson, MD", styles['Normal']))
    story.append(Paragraph("Internal Medicine", styles['Normal']))
    story.append(Paragraph(f"Date: October 20, 2024", styles['Normal']))
    
    doc.build(story)
    print(f"✅ Created: {filename}")


def create_prescription_pdf():
    """Create sample prescription PDF"""
    if not REPORTLAB_AVAILABLE:
        return
    
    filename = os.path.join(SCRIPT_DIR, "sample_prescription.pdf")
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#006633'))
    story.append(Paragraph("RIVERSIDE MEDICAL CENTER", title_style))
    story.append(Paragraph("Prescription Record", styles['Heading2']))
    story.append(Spacer(1, 0.2*inch))
    
    # Patient Info
    patient_data = [
        ["Patient Name:", "Maria Garcia"],
        ["DOB:", "07/22/1968"],
        ["Patient ID:", "PMC-789456"],
        ["Date:", "October 25, 2024"]
    ]
    t = Table(patient_data, colWidths=[1.5*inch, 4*inch])
    story.append(t)
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("<b>Allergies:</b> Penicillin", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Diagnoses
    story.append(Paragraph("<b>Current Diagnoses:</b>", styles['Heading3']))
    story.append(Paragraph("• Chronic Obstructive Pulmonary Disease (COPD)", styles['Normal']))
    story.append(Paragraph("• Coronary Artery Disease", styles['Normal']))
    story.append(Paragraph("• Gastroesophageal Reflux Disease (GERD)", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Prescriptions
    story.append(Paragraph("<b>PRESCRIPTIONS:</b>", styles['Heading3']))
    story.append(Spacer(1, 0.1*inch))
    
    prescriptions = [
        ("1. Albuterol Inhaler 90mcg", "2 puffs every 4-6 hours PRN"),
        ("2. Tiotropium (Spiriva) 18mcg", "Inhale 1 capsule once daily"),
        ("3. Clopidogrel (Plavix) 75mg", "Take 1 tablet PO once daily"),
        ("4. Metoprolol Succinate 50mg", "Take 1 tablet PO once daily"),
        ("5. Omeprazole 20mg", "Take 1 capsule PO once daily before breakfast"),
        ("6. Prednisone 10mg", "Take 1 tablet PO once daily for 5 days")
    ]
    
    for med, sig in prescriptions:
        story.append(Paragraph(f"<b>{med}</b>", styles['Normal']))
        story.append(Paragraph(f"   Sig: {sig}", styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Vital Signs
    story.append(Paragraph("<b>VITAL SIGNS:</b>", styles['Heading3']))
    vitals_data = [
        ["Blood Pressure:", "138/86 mmHg"],
        ["Pulse:", "72 bpm"],
        ["O2 Saturation:", "94% on room air"]
    ]
    t = Table(vitals_data, colWidths=[2*inch, 2*inch])
    story.append(t)
    story.append(Spacer(1, 0.3*inch))
    
    # Signature
    story.append(Paragraph("Prescriber: Dr. Michael Chen, MD", styles['Normal']))
    story.append(Paragraph("Cardiology & Pulmonology", styles['Normal']))
    story.append(Paragraph("DEA: MC1234567", styles['Normal']))
    story.append(Paragraph(f"Date: October 25, 2024", styles['Normal']))
    
    doc.build(story)
    print(f"✅ Created: {filename}")


def create_lab_results_pdf():
    """Create sample lab results PDF"""
    if not REPORTLAB_AVAILABLE:
        return
    
    filename = os.path.join(SCRIPT_DIR, "sample_lab_results.pdf")
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#990000'))
    story.append(Paragraph("METROPOLITAN LABORATORY SERVICES", title_style))
    story.append(Paragraph("Patient Lab Report", styles['Heading2']))
    story.append(Spacer(1, 0.2*inch))
    
    # Patient Info
    patient_data = [
        ["Patient Name:", "Robert Taylor"],
        ["DOB:", "11/30/1955"],
        ["Patient ID:", "LAB-2024-556677"],
        ["Collection Date:", "October 22, 2024"]
    ]
    t = Table(patient_data, colWidths=[2*inch, 4*inch])
    story.append(t)
    story.append(Spacer(1, 0.2*inch))
    
    # CBC
    story.append(Paragraph("<b>COMPLETE BLOOD COUNT (CBC):</b>", styles['Heading3']))
    cbc_data = [
        ["Test", "Result", "Reference Range"],
        ["WBC", "7.2 K/uL", "4.5-11.0"],
        ["RBC", "4.5 M/uL", "4.5-5.5"],
        ["Hemoglobin", "13.8 g/dL", "13.5-17.5"],
        ["Platelet Count", "245 K/uL", "150-400"]
    ]
    t = Table(cbc_data, colWidths=[2.5*inch, 1.5*inch, 2*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(t)
    story.append(Spacer(1, 0.2*inch))
    
    # Metabolic Panel
    story.append(Paragraph("<b>COMPREHENSIVE METABOLIC PANEL:</b>", styles['Heading3']))
    cmp_data = [
        ["Test", "Result", "Reference Range", "Flag"],
        ["Glucose", "185 mg/dL", "70-100", "HIGH"],
        ["Creatinine", "1.8 mg/dL", "0.7-1.3", "HIGH"],
        ["eGFR", "42 mL/min", ">60", "LOW"],
        ["Sodium", "138 mEq/L", "136-145", ""],
        ["Potassium", "4.8 mEq/L", "3.5-5.0", ""]
    ]
    t = Table(cmp_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('TEXTCOLOR', (3, 1), (3, 3), colors.red),  # HIGH/LOW flags in red
        ('FONTNAME', (3, 1), (3, 3), 'Helvetica-Bold')
    ]))
    story.append(t)
    story.append(Spacer(1, 0.2*inch))
    
    # Lipid Panel
    story.append(Paragraph("<b>LIPID PANEL:</b>", styles['Heading3']))
    lipid_data = [
        ["Test", "Result", "Reference Range", "Flag"],
        ["Total Cholesterol", "245 mg/dL", "<200", "HIGH"],
        ["LDL Cholesterol", "165 mg/dL", "<100", "HIGH"],
        ["HDL Cholesterol", "38 mg/dL", ">40", "LOW"],
        ["Triglycerides", "210 mg/dL", "<150", "HIGH"]
    ]
    t = Table(lipid_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('TEXTCOLOR', (3, 1), (3, -1), colors.red),
        ('FONTNAME', (3, 1), (3, -1), 'Helvetica-Bold')
    ]))
    story.append(t)
    story.append(Spacer(1, 0.2*inch))
    
    # HbA1c
    story.append(Paragraph("<b>HEMOGLOBIN A1C:</b>", styles['Heading3']))
    story.append(Paragraph("<b>HbA1c: 8.9%</b> (HIGH) (Normal: <5.7%)", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Critical Values
    story.append(Paragraph("<b>CRITICAL VALUES NOTED:</b>", styles['Heading3']))
    critical_style = ParagraphStyle('Critical', parent=styles['Normal'], textColor=colors.red)
    story.append(Paragraph("1. Elevated Blood Glucose (185 mg/dL)", critical_style))
    story.append(Paragraph("2. Elevated Creatinine (1.8 mg/dL) - Reduced kidney function", critical_style))
    story.append(Paragraph("3. Low eGFR (42) - Stage 3 Chronic Kidney Disease", critical_style))
    story.append(Paragraph("4. Elevated HbA1c (8.9%) - Poor diabetes control", critical_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Impressions
    story.append(Paragraph("<b>IMPRESSIONS:</b>", styles['Heading3']))
    story.append(Paragraph("• Poorly controlled Type 2 Diabetes Mellitus", styles['Normal']))
    story.append(Paragraph("• Stage 3 Chronic Kidney Disease (Moderate)", styles['Normal']))
    story.append(Paragraph("• Dyslipidemia", styles['Normal']))
    story.append(Paragraph("• Recommend nephrology consultation", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Signature
    story.append(Paragraph("Laboratory Director: Dr. James Wilson, MD", styles['Normal']))
    story.append(Paragraph("Report Verified: October 23, 2024", styles['Normal']))
    
    doc.build(story)
    print(f"✅ Created: {filename}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("📄 GENERATING SAMPLE MEDICAL PDF FILES")
    print("="*60 + "\n")
    
    if REPORTLAB_AVAILABLE:
        print("Creating sample PDFs...")
        create_medical_report_pdf()
        create_prescription_pdf()
        create_lab_results_pdf()
        print("\n✅ All PDF files generated successfully!")
        print(f"📁 Location: {SCRIPT_DIR}")
    else:
        print("\n⚠️  To generate PDFs, install ReportLab:")
        print("   pip install reportlab")
        print("\n📝 Text versions are already available:")
        print("   - sample_medical_report_1.txt")
        print("   - sample_prescription.txt")
        print("   - sample_lab_results.txt")
    
    print("\n" + "="*60)
    print("You can now use these files to test document upload!")
    print("="*60 + "\n")

