#!/usr/bin/env python3
"""
Ollama Python Integration Test Script
Tests three different methods to interact with local Ollama models.
"""

import json
import sys
from typing import List, Dict, Generator, AsyncGenerator, Union

# Try to import the official client first – if unavailable, fall back to raw HTTP.
try:
    import ollama
    HAS_OLLAMA_CLIENT = True
except Exception:
    HAS_OLLAMA_CLIENT = False
    ollama = None

# --------------------------------------------------------------
class OllamaWrapper:
    """
    Simple wrapper that abstracts:
      • Official client (`ollama`) when installed
      • Plain `requests` otherwise
    Supports both normal and streaming responses.
    """
    def __init__(
        self,
        model: str = "llama2",
        base_url: str = "http://127.0.0.1:11434",
        timeout: float = 30.0,
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    # ---------------------- public API -------------------------
    def chat(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
    ) -> Union[Dict, Generator[str, None, None]]:
        """
        :param messages: list of {"role": "...", "content": "..."} dicts
        :param stream:   if True, returns a generator yielding token chunks
        :return:        dict (non‑stream) or generator (stream)
        """
        # 1️⃣ Prefer the official client if available
        if HAS_OLLAMA_CLIENT:
            if stream:
                return (
                    chunk["message"]["content"]
                    for chunk in ollama.chat(model=self.model, messages=messages, stream=True)
                )
            else:
                resp = ollama.chat(model=self.model, messages=messages)
                return resp

        # 2️⃣ Otherwise use raw HTTP
        payload = {"model": self.model, "messages": messages, "stream": stream}
        import requests
        url = f"{self.base_url}/api/chat"
        resp = requests.post(url, json=payload, stream=stream, timeout=self.timeout)
        resp.raise_for_status()

        if not stream:
            return resp.json()

        # Streaming mode – yield incremental token strings
        for line in resp.iter_lines(decode_unicode=True):
            if not line:
                continue
            data = json.loads(line)
            yield data["message"]["content"]

# --------------------------------------------------------------
# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("🤖 Ollama Python Integration Test")
    print("=" * 60)
    print()
    
    # Check if Ollama client is available
    if HAS_OLLAMA_CLIENT:
        print("✅ Official ollama client is installed and ready")
    else:
        print("⚠️  Official ollama client not found, will use requests library")
    print()
    
    # Try to get available models
    try:
        if HAS_OLLAMA_CLIENT:
            models_list = ollama.list()
            model_objects = models_list.get('models', [])
            available_models = [m.model for m in model_objects if hasattr(m, 'model')]
            print(f"📦 Available local models: {available_models}")
            
            if available_models:
                # Use llama2 if available, otherwise first model
                test_model = "llama2:latest" if "llama2" in available_models[0].lower() else available_models[0]
            else:
                print("❌ No models found locally. Please pull a model first:")
                print("   Example: ollama pull llama2")
                sys.exit(1)
            
    except Exception as e:
        print(f"⚠️  Could not list models: {e}")
        test_model = "llama2:latest"  # Default fallback
        print(f"   Will try to use: {test_model}")
    
    print()
    print(f"🔧 Using model: {test_model}")
    print()
    
    # Initialize wrapper
    wrapper = OllamaWrapper(model=test_model)

    try:
        # ---- 1️⃣ Non‑streaming example ----
        print("=" * 60)
        print("1️⃣ Testing Non‑streaming Response")
        print("=" * 60)
        
        out = wrapper.chat(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello in one sentence."},
            ],
            stream=False,
        )
        print("Response:")
        print("-" * 60)
        
        # Debug: print the type first
        print(f"[DEBUG] Response type: {type(out)}")
        
        # The wrapper returns the response dict from ollama.chat()
        if isinstance(out, dict):
            print(f"[DEBUG] Response keys: {out.keys()}")
            if "message" in out and isinstance(out["message"], dict) and "content" in out["message"]:
                print(out["message"]["content"])
            elif "content" in out:
                print(out["content"])
            else:
                print("Full response:", out)
        elif hasattr(out, '__iter__') and not isinstance(out, str):
            # It's a generator somehow
            print("[DEBUG] Converting generator to string...")
            result = ''.join(out)
            print(result)
        else:
            print("[DEBUG] Unknown response type")
            print("Response object:", type(out))
            print(out)
        print()

        # ---- 2️⃣ Streaming example ----
        print("=" * 60)
        print("2️⃣ Testing Streaming Response (token‑by‑token)")
        print("=" * 60)
        print("Response (streaming):")
        print("-" * 60)
        for token in wrapper.chat(
            messages=[{"role": "user", "content": "Write a 2-line poem about AI."}],
            stream=True,
        ):
            print(token, end="", flush=True)
        print()
        print()

        # ---- 3️⃣ Method 2: Direct HTTP with requests ----
        print("=" * 60)
        print("3️⃣ Testing Direct HTTP Method")
        print("=" * 60)
        
        import requests
        
        url = "http://127.0.0.1:11434/api/chat"
        payload = {
            "model": test_model,
            "messages": [
                {"role": "system", "content": "You are a concise writer."},
                {"role": "user", "content": "Summarize machine learning in 1 sentence."}
            ],
            "stream": False  # Explicitly disable streaming
        }
        
        r = requests.post(url, json=payload, timeout=30)
        r.raise_for_status()
        
        # Try to parse as regular JSON first
        try:
            response = r.json()
            print("Response:")
            print("-" * 60)
            print(response["message"]["content"])
        except json.JSONDecodeError:
            # If it's NDJSON, just read the first line
            lines = r.text.strip().split('\n')
            if lines:
                first_response = json.loads(lines[0])
                print("Response (from NDJSON):")
                print("-" * 60)
                print(first_response.get("message", {}).get("content", ""))
        
        print()
        
        print("=" * 60)
        print("✅ All tests completed successfully!")
        print("=" * 60)
        
    except ConnectionError as e:
        print("❌ Connection Error: Could not connect to Ollama server.")
        print("   Make sure Ollama is running: ollama serve")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

