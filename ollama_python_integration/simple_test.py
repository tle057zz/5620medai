#!/usr/bin/env python3
"""
Simple Ollama Python Test - Quick verification
"""

import ollama

print("=" * 60)
print("🤖 Ollama Python Integration - Simple Test")
print("=" * 60)
print()

# List available models
print("📦 Available models:")
try:
    models = ollama.list()
    model_list = models.get('models', [])
    
    for model in model_list:
        # Models are Model objects with .model attribute for name
        name = model.model if hasattr(model, 'model') else str(model)
        size = model.size if hasattr(model, 'size') else 'unknown'
        modified = model.modified_at if hasattr(model, 'modified_at') else 'unknown'
        
        print(f"  - {name}")
        print(f"    Size: {size}")
        print(f"    Modified: {modified}")
    
    # Use the first model
    if model_list:
        first_model = model_list[0]
        test_model = first_model.model if hasattr(first_model, 'model') else 'llama2'
        print()
        print(f"🔧 Testing with model: {test_model}")
        print()
        
        # Test 1: Simple non-streaming chat
        print("=" * 60)
        print("Test 1: Non-streaming chat")
        print("=" * 60)
        
        response = ollama.chat(
            model=test_model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello in one sentence."}
            ]
        )
        
        print("Response:")
        print(response['message']['content'])
        print()
        
        # Test 2: Streaming chat
        print("=" * 60)
        print("Test 2: Streaming chat (token-by-token)")
        print("=" * 60)
        print("Streaming response: ", end="", flush=True)
        
        for chunk in ollama.chat(
            model=test_model,
            messages=[{"role": "user", "content": "Count from 1 to 5 in one word per number."}],
            stream=True
        ):
            print(chunk['message']['content'], end='', flush=True)
        
        print()
        print()
        print("=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        
    else:
        print("❌ No models available. Please pull a model first:")
        print("   ollama pull llama2")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

