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
