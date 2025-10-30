#!/usr/bin/env python3
"""
Working Ollama Test - Simplified version that actually works
"""

import ollama

print("=" * 60)
print("🤖 Ollama Working Test")
print("=" * 60)
print()

# Get available models
models = ollama.list()
model_list = models.get('models', [])

if not model_list:
    print("❌ No models found. Run: ollama pull llama2")
    exit(1)

# Use first model
model_name = model_list[0].model
print(f"📦 Using model: {model_name}")
print()

# Test 1: Simple chat
print("=" * 60)
print("Test 1: Non-streaming")
print("=" * 60)
response = ollama.chat(
    model=model_name,
    messages=[{"role": "user", "content": "Say 'Hello World' in one sentence."}]
)
print("Response:", response['message']['content'])
print()

# Test 2: Streaming
print("=" * 60)
print("Test 2: Streaming")
print("=" * 60)
print("Response: ", end="", flush=True)
for chunk in ollama.chat(
    model=model_name,
    messages=[{"role": "user", "content": "Count 1, 2, 3"}],
    stream=True
):
    print(chunk['message']['content'], end='', flush=True)
print()
print()

print("=" * 60)
print("✅ All tests passed!")
print("=" * 60)


