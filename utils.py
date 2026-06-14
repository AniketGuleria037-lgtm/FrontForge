import requests
import json
import re

OLLAMA_URL         = "http://localhost:11434/api/generate"
MODEL              = "qwen3:8b"

def call_ollama(user_prompt, system_prompt):
    print("Calling Ollama... this may take 1-3 minutes")
    
    payload = {
        "model": MODEL,
        "system": system_prompt,
        "prompt": f"Build this React app and return ONLY JSON: {user_prompt}",
        "stream": False,
        "think": False,
        "format": "json",
        "options": {
            "temperature": 0.1,
            "num_ctx": 8192,
            "num_predict": 8192
        }
    }
    
    response = requests.post(OLLAMA_URL, json=payload, timeout=900)
    raw = response.json()["response"]
    print(f"Received {len(raw)} characters from model")
    return raw

def parse_response(raw):
    if not raw or raw.strip() == "":
        print("ERROR: Empty response from model")
        return None

    # Remove thinking tags
    text = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL).strip()

    # Remove markdown fences
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1]).strip()

    # Find where JSON starts
    start = text.find("{")
    if start == -1:
        print("ERROR: No JSON found in response")
        print("Raw output:", raw[:200])
        return None
    text = text[start:]

    # Find where JSON ends using depth counter
    depth = 0
    end = -1
    for i, ch in enumerate(text):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break

    if end == -1:
        print("WARNING: JSON not properly closed - attempting salvage")
        # Add closing braces to fix truncated JSON
        open_braces = text.count("{") - text.count("}")
        open_brackets = text.count("[") - text.count("]")
        text = text + ("]" * open_brackets) + ("}" * open_braces)
        end = len(text)

    # Try parsing
    try:
        data = json.loads(text[:end])
        print("Parsed response successfully")
        return data
    except json.JSONDecodeError as e:
        print(f"WARNING: JSON parse failed ({e}) - attempting salvage")
        try:
            # Find last complete closing brace
            last_brace = text.rfind('}')
            if last_brace != -1:
                data = json.loads(text[:last_brace+1])
                print("Parsed response successfully (salvaged)")
                return data
        except json.JSONDecodeError:
            pass
        print("ERROR: Could not parse JSON response")
        print("Problematic text:", text[:300])
        return None

if __name__ == "__main__":
    print("utils loaded successfully")