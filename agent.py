import os
import json
import re
import subprocess
import shutil
import requests
from pathlib import Path

# ── Configuration ──────────────────────────────────────
OLLAMA_URL         = "http://localhost:11434/api/generate"
MODEL              = "qwen3:4b"
OUTPUT_DIR         = Path("generated-app")
SYSTEM_PROMPT_FILE = Path("prompts/system_prompt.txt")
MAX_RETRIES        = 3

def load_system_prompt():
    if not SYSTEM_PROMPT_FILE.exists():
        print("ERROR: system_prompt.txt not found")
        exit(1)
    return SYSTEM_PROMPT_FILE.read_text(encoding="utf-8")

def call_ollama(user_prompt, system_prompt):
    print("Calling Ollama... this may take 1-3 minutes")
    
    payload = {
        "model": MODEL,
        "system": system_prompt,
        "prompt": user_prompt,
        "stream": False,
        "think": False,
        "options": {
            "temperature": 0.2,
            "num_ctx": 4096,
            "num_predict": 4096
        }
    }
    
    response = requests.post(OLLAMA_URL, json=payload, timeout=300)
    raw = response.json()["response"]
    print(f"Received {len(raw)} characters from model")
    return raw

def parse_response(raw):
    print("Parsing model response...")
    
    # Remove Qwen3 thinking tags if present
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
    print(f"Parsed {len(data['files'])} files successfully")
    return data

def write_files(data):
    print(f"Writing files to {OUTPUT_DIR}/")
    
    # Delete old generated app if exists
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True)
    
    # Write each file
    for file in data["files"]:
        file_path = OUTPUT_DIR / file["path"]
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        content = file["content"]
        content = content.replace("\\n", "\n").replace("\\t", "\t")
        
        file_path.write_text(content, encoding="utf-8")
        print(f"  Wrote: {file['path']}")

def write_package_json(data):
    print("Writing package.json...")
    
    package_json = {
        "name": data.get("project_name", "frontforge-app"),
        "private": True,
        "version": "0.0.1",
        "type": "module",
        "scripts": {
            "dev":     "vite",
            "build":   "vite build",
            "preview": "vite preview"
        },
        "dependencies": {
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
            **data.get("dependencies", {})
        },
        "devDependencies": {
            "@vitejs/plugin-react": "^4.0.0",
            "vite": "^5.0.0",
            "tailwindcss": "^3.4.0",
            "autoprefixer": "^10.4.0",
            "postcss": "^8.4.0",
            **data.get("devDependencies", {})
        }
    }
    
    path = OUTPUT_DIR / "package.json"
    path.write_text(json.dumps(package_json, indent=2), encoding="utf-8")
    print("package.json written")