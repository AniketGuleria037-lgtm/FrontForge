import requests
import json
import re

OLLAMA_URL         = "http://localhost:11434/api/generate"
MODEL              = "qwen3:4b"

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
            "num_ctx": 6144,
            "num_predict": 6144
        }
    }
    
    response = requests.post(OLLAMA_URL, json=payload, timeout=600)
    raw = response.json()["response"]
    print(f"Received {len(raw)} characters from model")
    return raw

def parse_response(raw):
    print("Parsing model response...")
    
    text = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL).strip()
    
    # Remove markdown code fences if present
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1]).strip()
    
    # Find the start of JSON
    start = text.find("{")
    if start == -1:
        print("ERROR: No JSON found in response")
        print("Raw output was:", raw[:300])
        exit(1)
    text = text[start:]
    
    # Find the end of JSON
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
    
    data = json.loads(text[:end])
    print("Parsed response successfully")
    return data

if __name__ == "__main__":
    print("utils loaded successfully")