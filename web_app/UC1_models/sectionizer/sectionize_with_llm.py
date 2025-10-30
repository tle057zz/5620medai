#!/usr/bin/env python3
"""
Sectionizer with LLM (Ollama GPT-OSS or other models)
Intelligently identifies sections in medical PDFs using AI
"""

import ollama
import json
import os
import re
from typing import Dict


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF file using pdfplumber"""
    import pdfplumber
    
    print(f"📄 Extracting text from: {pdf_path}")
    text = ""
    
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
            if i < 3:  # Progress indicator
                print(f"   Page {i+1}...", end=" ", flush=True)
    
    print(f"\n✅ Extracted {len(text)} characters")
    return text


def sectionize_with_llm(text: str, model: str = "llama2:latest") -> Dict[str, str]:
    """
    Use Ollama LLM to identify sections in medical text
    
    Args:
        text: The text to sectionize
        model: The Ollama model name
    
    Returns:
        Dictionary mapping section titles to content
    """
    
    print(f"\n🤖 Using LLM model: {model}")
    
    # Simple approach: Ask LLM to identify section headers
    prompt = f"""Analyze this medical document and identify all distinct sections.

Instructions:
1. Look for section headers like "PATIENT INFORMATION", "MEDICAL HISTORY", "DIAGNOSIS", etc.
2. List each section title and its content
3. Return as JSON with format: {{"Section Title": "content", "Another Section": "content"}}

Document text:
{text[:4000]}  # Limit to avoid token limits
"""
    
    try:
        print("🔄 Querying LLM...")
        
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": "You are a medical document analyst. Extract sections and return ONLY valid JSON."},
                {"role": "user", "content": prompt}
            ],
            stream=False
        )
        
        content = response['message']['content']
        print("✅ Received LLM response")
        
        # Clean JSON from markdown code blocks
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        # Parse JSON
        try:
            sections = json.loads(content)
            print(f"✅ Parsed {len(sections)} sections")
            return sections
        except json.JSONDecodeError as e:
            print(f"⚠️  JSON parse error: {e}")
            print(f"Response preview: {content[:200]}...")
            
            # Fallback: regex-based sectionization
            print("📝 Falling back to regex-based sectionization...")
            return regex_sectionize(text)
            
    except Exception as e:
        print(f"❌ LLM error: {e}")
        print("📝 Falling back to regex-based sectionization...")
        return regex_sectionize(text)


def regex_sectionize(text: str) -> Dict[str, str]:
    """Fallback: Simple regex-based sectionization"""
    sections = {}
    
    # Look for common medical section headers
    patterns = [
        (r'(PATIENT\s+(?:INFORMATION|DETAILS|DATA))', re.IGNORECASE),
        (r'(MEDICAL\s+(?:HISTORY|BACKGROUND))', re.IGNORECASE),
        (r'(DIAGNOSIS|DIAGNOSTIC\s+(?:RESULTS|FINDINGS))', re.IGNORECASE),
        (r'(PRESCRIPTION|MEDICATION|TREATMENT)', re.IGNORECASE),
        (r'(OBSERVATIONS|NOTES|COMMENTS)', re.IGNORECASE),
    ]
    
    # Split by headers
    current_section = "INTRODUCTION"
    sections[current_section] = ""
    
    lines = text.split('\n')
    for line in lines:
        # Check if this line is a header
        is_header = False
        for pattern, flags in patterns:
            if re.search(pattern, line, flags):
                current_section = re.search(pattern, line, flags).group(1).upper()
                sections[current_section] = ""
                is_header = True
                break
        
        if not is_header:
            sections[current_section] += line + "\n"
    
    # Clean empty sections
    return {k: v.strip() for k, v in sections.items() if v.strip()}


def sectionize_pdf(pdf_path: str, model: str = None, output_path: str = None) -> Dict[str, str]:
    """
    Complete workflow: PDF → Text → Sectionized sections
    
    Args:
        pdf_path: Input PDF file
        model: Ollama model (defaults to first available)
        output_path: Where to save JSON output
    
    Returns:
        Dictionary of sections
    """
    
    # Get model
    if not model:
        try:
            models = ollama.list()
            if models.get('models'):
                model = models['models'][0].model
            else:
                model = "llama2:latest"
        except:
            model = "llama2:latest"
    
    print("=" * 70)
    print("🏥 PDF Sectionizer with LLM")
    print("=" * 70)
    print(f"📄 Input: {pdf_path}")
    print(f"🤖 Model: {model}")
    print()
    
    # Step 1: Extract text
    text = extract_text_from_pdf(pdf_path)
    
    # Step 2: Sectionize
    sections = sectionize_with_llm(text, model)
    
    # Step 3: Save
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(sections, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Saved to: {output_path}")
    
    return sections


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python sectionize_with_llm.py <pdf_file>")
        print("\nExample:")
        print("  python sectionize_with_llm.py ../../samples/sample_medical_report_1.pdf")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        sys.exit(1)
    
    output_path = pdf_path.replace('.pdf', '_sections.json')
    
    sections = sectionize_pdf(pdf_path, output_path=output_path)
    
    print("\n" + "=" * 70)
    print(f"✅ Complete! Found {len(sections)} sections")
    print("=" * 70)
    
    for section_name in sections.keys():
        print(f"  ✓ {section_name}")

