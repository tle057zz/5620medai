# Sectionizing PDFs with Ollama/GPT-OSS

This directory now includes an AI-powered sectionizer that uses Ollama models (including GPT-OSS) to intelligently identify sections in medical PDF documents.

## 🚀 Quick Start

### Prerequisites
1. Ollama installed and running
2. At least one model pulled (llama2, gpt-oss, etc.)
3. Python packages: `ollama`, `pdfplumber`

### Basic Usage

```bash
# Navigate to the sectionizer directory
cd ai_medical/sectionizer

# Run the AI sectionizer on a PDF
python sectionize_with_llm.py ../../samples/sample_medical_report_1.pdf
```

### What It Does

1. **Extracts text** from the PDF using pdfplumber
2. **Uses Ollama LLM** to intelligently identify section boundaries
3. **Returns structured JSON** with section titles and content
4. **Falls back to regex** if LLM parsing fails

## 📋 Example Output

```json
{
  "PATIENT INFORMATION": "Name: John Doe\nAge: 45\n...",
  "MEDICAL HISTORY": "Patient has history of...",
  "DIAGNOSIS": "Acute upper respiratory infection...",
  "PRESCRIPTION": "Amoxicillin 500mg, twice daily..."
}
```

## 🎯 Features

### ✨ LLM-Powered Sectionization
- Uses natural language understanding to identify sections
- Handles variations in section headers
- Adapts to different document formats

### 🔄 Fallback Mechanism
- If LLM parsing fails, uses regex-based patterns
- Looks for common medical section headers
- Ensures you always get structured output

### 💾 Output Format
- Saves results as JSON files
- Easy to integrate with other pipeline components
- Human-readable output

## 📝 Usage Examples

### Example 1: Basic Sectionization

```bash
python sectionize_with_llm.py sample_medical_report_1.pdf
# Output: sample_medical_report_1_sections.json
```

### Example 2: Using Specific Model

Modify the script to specify a model:
```python
sections = sectionize_pdf(
    pdf_path="document.pdf",
    model="gpt-oss:120b-cloud",  # Your preferred model
    output_path="sections.json"
)
```

### Example 3: Python Integration

```python
from sectionizer.sectionize_with_llm import sectionize_pdf

# Sectionize a PDF
sections = sectionize_pdf(
    pdf_path="medical_report.pdf",
    output_path="output.json"
)

# Access sections
for section_name, content in sections.items():
    print(f"{section_name}: {content[:100]}...")
```

## 🔧 Available Models

Test with different models to see which works best:

```bash
# List available models
ollama list

# Pull a new model
ollama pull llama2
ollama pull mixtral
ollama pull phi3
```

## ⚙️ Configuration

### Adjusting Text Length

If dealing with very long documents, you may need to adjust the token limit:

```python
# In sectionize_with_llm.py
text_length_limit = 4000  # Increase for longer documents
```

### Improving Accuracy

For better results:
1. Use larger models (7B+ parameters)
2. Provide more context in the prompt
3. Clean the PDF text before sectionizing

## 🆘 Troubleshooting

### Error: "No models found"
```bash
ollama pull llama2
```

### Error: "PDF extraction failed"
- Ensure pdfplumber is installed: `pip install pdfplumber`
- Check if PDF is not corrupted
- Try converting PDF to text first

### Error: "JSON parse failed"
- This triggers automatic fallback to regex
- Check the console for warnings
- Try a different model

## 🔄 Integration with Pipeline

You can integrate this with the existing medical AI pipeline:

```python
# In your pipeline
from ai_medical.sectionizer.sectionize_with_llm import sectionize_pdf

# After OCR
sections = sectionize_pdf("ocr_output.txt", output_path="sections.json")

# Use sections for NER, linking, etc.
for section_name, content in sections.items():
    entities = extract_entities(content)
    # Process entities...
```

## 📊 Comparison

| Method | Speed | Accuracy | Flexibility |
|--------|-------|----------|-------------|
| Regex-based | Fast | Medium | Low |
| **LLM-based** | **Medium** | **High** | **High** |

## 🎯 Best Practices

1. **Start with small documents** to test
2. **Use appropriate models** for your task
3. **Monitor token usage** for cost control
4. **Implement caching** for repeated documents
5. **Validate output** before using downstream

## 📚 Next Steps

- Integrate with NER module
- Add to web application
- Implement batch processing
- Add section validation rules

---

**Status**: ✅ Ready to use!  
**Last Updated**: 2025-10-28


