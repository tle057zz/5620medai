#!/usr/bin/env python3
"""
Sectionizer with Ollama LLM
Uses GPT-OSS or other Ollama models to intelligently sectionize medical documents
"""

import ollama
import json
import os
from typing import Dict, List
import pdfplumber


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF file"""
    print(f"📄 Extracting text from PDF: {pdf_path}")
    
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    
    print(f"✅ Extracted {len(text)} characters from PDF")
    return text


def sectionize_with_ollama(text: str, model: str = "llama2:latest") -> Dict[str, str]:
    """
    Use Ollama LLM to intelligently sectionize medical text
    
    Args:
        text: The full text to sectionize
        model: The Ollama model to use
    
    Returns:
        Dictionary with section names as keys and content as values
    """
    
    print(f"🤖 Sectionizing with model: {model}")
    
    # Create a prompt for the LLM
    prompt = f"""You are a medical document sectionizer. Your task is to identify and extract distinct sections from medical documents.

Given the following text, identify all major sections and return them in JSON format with the section title as the key and the content as the value.

Text to sectionize:
{text[:2000]}..."""  # Limit to first 2000 chars to avoid token limits

    # For streaming: get the response
    print("🔄 Asking LLM to identify sections...")
    
    try:
        response = ollama.chat(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a medical document expert. Analyze medical documents and identify distinct sections. Return ONLY valid JSON in this format: {\"Section Name\": \"content\", \"Another Section\": \"content\"}"
                },
                {
                    "role": "user",
                    "content": f"""Analyze this medical document text and identify all distinct sections. 
Return ONLY valid JSON format with section titles as keys and their content as values.

Text:
{text[:3000]}  # Limit input to avoid token limits"""
                }
            ]
        )
        
        print("✅ Received response from LLM")
        
        # Extract content from response
        content = response['message']['content']
        
        # Try to parse as JSON
        try:
            # Clean the content - remove markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            sections = json.loads(content)
            print(f"✅ Successfully parsed {len(sections)} sections")
            return sections
            
        except json.JSONDecodeError as e:
            print(f"⚠️  Could not parse as JSON: {e}")
            print(f"Raw response: {content[:500]}")
            
            # Fallback: try to extract sections manually
            return {"FULL_TEXT": text}
            
    except Exception as e:
        print(f"❌ Error calling Ollama: {e}")
        return {"FULL_TEXT": text}


def sectionize_pdf(pdf_path: str, model: str = "llama2:latest", output_path: str = None) -> Dict[str, str]:
    """
    Complete workflow: Extract text from PDF and sectionize it with Ollama
    
    Args:
        pdf_path: Path to input PDF
        model: Ollama model to use
        output_path: Optional path to save JSON output
    
    Returns:
        Dictionary of sections
    """
    
    # Step 1: Extract text from PDF
    text = extract_text_from_pdf(pdf_path)
    
    # Step 2: Sectionize with Ollama
    sections = sectionize_with_ollama(text, model)
    
    # Step 3: Save output if requested
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(sections, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved sectionized output to: {output_path}")
    
    return sections


if __name__ == "__main__":
    import sys
    
    # Get available models
    try:
        models = ollama.list()
        model_list = models.get('models', [])
        if model_list:
            model_name = model_list[0].model
            print(f"📦 Available model: {model_name}")
        else:
            print("❌ No models found. Run: ollama pull llama2")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error getting models: {e}")
        model_name = "llama2:latest"  # fallback
    
    # Example usage
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        
        if not os.path.exists(pdf_path):
            print(f"❌ File not found: {pdf_path}")
            sys.exit(1)
        
        # Determine output path
        output_path = pdf_path.replace('.pdf', '_sections.json')
        
        print("=" * 60)
        print("🏥 PDF Sectionizer with Ollama")
        print("=" * 60)
        print()
        
        # Process the PDF
        sections = sectionize_pdf(
            pdf_path=pdf_path,
            model=model_name,
            output_path=output_path
        )
        
        print()
        print("=" * 60)
        print(f"✅ Successfully extracted {len(sections)} sections")
        print("=" * 60)
        
        # Print sections
        print("\nDetected sections:")
        for section_name in sections.keys():
            print(f"  - {section_name}")
    
    else:
        print("Usage: python sectionize_with_ollama.py <path_to_pdf>")
        print("\nExample:")
        print("  python sectionize_with_ollama.py ../samples/sample_medical_report_1.pdf")

