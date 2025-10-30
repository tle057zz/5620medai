# Ollama Python Integration

This directory contains examples and utilities for integrating Ollama (local LLM) with Python.

## ✅ Setup Complete

Ollama is installed and the Python client is ready to use!

### Installed Components

- **Ollama Client**: Installed via `pip install ollama`
- **Requests Library**: Installed for HTTP fallback
- **Available Model**: `gpt-oss:120b-cloud` (116.8B parameters)

## 📁 Files

- `ollama_test.py` - Comprehensive test script with wrapper class
- `simple_test.py` - Quick verification script
- `README.md` - This file

## 🚀 Quick Start

### 1. Basic Usage

```python
import ollama

# Simple chat
response = ollama.chat(
    model="gpt-oss:120b-cloud",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response['message']['content'])
```

### 2. Streaming Response

```python
import ollama

# Streaming (token-by-token)
for chunk in ollama.chat(
    model="gpt-oss:120b-cloud",
    messages=[{"role": "user", "content": "Tell me a joke"}],
    stream=True
):
    print(chunk['message']['content'], end='', flush=True)
```

### 3. Run the Test Scripts

```bash
# Simple test
python3 ollama_python_integration/simple_test.py

# Advanced test
python3 ollama_python_integration/ollama_test.py
```

## 🔧 Available Models

Check what models are installed:

```bash
ollama list
```

Pull new models:

```bash
ollama pull llama2
ollama pull mixtral
ollama pull phi3
```

## 📊 Usage Examples

### Example 1: Simple Chat

```python
import ollama

response = ollama.chat(
    model="gpt-oss:120b-cloud",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is machine learning?"}
    ]
)
print(response['message']['content'])
```

### Example 2: Medical Document Analysis

```python
import ollama

# Analyze medical text
medical_text = "Patient presents with chest pain and shortness of breath."

response = ollama.chat(
    model="gpt-oss:120b-cloud",
    messages=[
        {"role": "system", "content": "You are a medical assistant. Analyze and summarize medical information."},
        {"role": "user", "content": f"Analyze this medical information: {medical_text}"}
    ]
)
print(response['message']['content'])
```

### Example 3: Stream with System Prompt

```python
import ollama

print("Generating explanation...")
for chunk in ollama.chat(
    model="gpt-oss:120b-cloud",
    messages=[
        {"role": "system", "content": "You explain complex topics in simple terms."},
        {"role": "user", "content": "Explain quantum computing in 3 sentences."}
    ],
    stream=True
):
    print(chunk['message']['content'], end='', flush=True)
print()  # New line
```

## 🎯 Integration with Medical AI Pipeline

You can integrate Ollama into your medical document processing pipeline:

```python
# In ai_medical/explain/generate_explanation.py
import ollama

def generate_llm_explanation(medical_text):
    response = ollama.chat(
        model="gpt-oss:120b-cloud",
        messages=[
            {"role": "system", "content": "You are a medical assistant that explains complex medical information in simple, patient-friendly language."},
            {"role": "user", "content": f"Explain this medical information: {medical_text}"}
        ]
    )
    return response['message']['content']
```

## 🔍 Troubleshooting

### Issue: "Connection refused"
- **Solution**: Make sure Ollama server is running
  ```bash
  ollama serve
  ```

### Issue: "Model not found"
- **Solution**: Pull the model first
  ```bash
  ollama pull <model-name>
  ```

### Issue: Import Error
- **Solution**: Install the ollama Python package
  ```bash
  pip install ollama
  ```

## 📚 API Reference

### Main Functions

#### `ollama.chat()`
Generate a chat completion.

**Parameters:**
- `model` (str): Model name
- `messages` (list): List of message dicts with 'role' and 'content'
- `stream` (bool): Whether to stream the response

**Returns:**
- Dict with 'message' containing the response (non-streaming)
- Generator yielding chunks (streaming)

#### `ollama.list()`
List available models.

**Returns:**
- Dict with 'models' containing list of model info

## 🌐 Advanced: HTTP API

If you prefer to use HTTP directly instead of the Python client:

```python
import requests

url = "http://127.0.0.1:11434/api/chat"
payload = {
    "model": "gpt-oss:120b-cloud",
    "messages": [{"role": "user", "content": "Hello"}]
}

r = requests.post(url, json=payload)
response = r.json()
print(response['message']['content'])
```

## 📖 Resources

- [Ollama Official Docs](https://ollama.com)
- [Ollama GitHub](https://github.com/ollama/ollama)
- [Python Client Docs](https://github.com/ollama/ollama-python)

---

**Status**: ✅ Ready to use!  
**Last Updated**: 2025


