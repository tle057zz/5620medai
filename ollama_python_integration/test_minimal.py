#!/usr/bin/env python3
"""
Minimal Ollama Test - Just verify it works
"""

import ollama

print("🤖 Testing Ollama...")
print()

# Get available models
try:
    models = ollama.list()
    print(f"📦 Found {len(models.get('models', []))} model(s)")
    
    # Get first model
    model_list = models.get('models', [])
    if not model_list:
        print("❌ No models found. Run: ollama pull llama2")
        exit(1)
    
    # Access model name correctly (it's a Model object, not a dict)
    model = model_list[0]
    model_name = model.model if hasattr(model, 'model') else str(model)
    
    print(f"🔧 Using model: {model_name}")
    print()
    
    # Test 1: Simple chat
    print("Test 1: Simple chat")
    print("-" * 40)
    response = ollama.chat(
        model=model_name,
        messages=[{"role": "user", "content": "Say 'Hello' in one word."}]
    )
    print(f"Response: {response['message']['content']}")
    print()
    
    # Test 2: Streaming
    print("Test 2: Streaming")
    print("-" * 40)
    print("Response: ", end="", flush=True)
    for chunk in ollama.chat(
        model=model_name,
        messages=[{"role": "user", "content": "Say 'World' in one word."}],
        stream=True
    ):
        print(chunk['message']['content'], end='', flush=True)
    print()
    print()
    
    print("✅ All tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

