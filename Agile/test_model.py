import subprocess
import json

def list_ollama_models():
    """List all models currently available in Ollama locally."""
    try:
        # Run the Ollama command to list models in JSON format
        result = subprocess.run(
            ["ollama", "list", "--json"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )

        # Parse JSON output (one model per line)
        models = [json.loads(line) for line in result.stdout.strip().splitlines()]
        return models

    except subprocess.CalledProcessError as e:
        print("Error running ollama list:", e.stderr)
        return []
    except json.JSONDecodeError:
        print("Failed to parse ollama output.")
        return []

# Example usage
if __name__ == "__main__":
    models = list_ollama_models()
    if models:
        print("✅ Local Ollama models available:")
        for m in models:
            print(f"- {m['name']} (size: {m.get('size', 'N/A')}, modified: {m.get('modified_at', 'N/A')})")
    else:
        print("⚠️ No local models found or Ollama not installed.")
