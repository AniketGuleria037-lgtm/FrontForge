import os
import json
import re
import subprocess
import shutil
import requests
from pathlib import Path

# ── Configuration ──────────────────────────────────────
OLLAMA_URL         = "http://localhost:11434/api/generate"
MODEL              = "qwen3:8b"
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
        "prompt": f"Build this React app and return ONLY JSON: {user_prompt}",
        "stream": False,
        "think": False,
        "format": "json",
        "options": {
            "temperature": 0.1,
            "num_ctx": 4096,
            "num_predict": 4096
        }
    }
    
    response = requests.post(OLLAMA_URL, json=payload, timeout=900)
    raw = response.json()["response"]
    print(f"Received {len(raw)} characters from model")
    return raw

def parse_response(raw):
    print("Parsing model response...")
    print("RAW OUTPUT FIRST 200 CHARS:", raw[:200])
    
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
            "react-router-dom": "^6.8.0",
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

def ensure_config_files():
    print("Checking config files...")
    
    defaults = {
        "vite.config.js": (
            "import { defineConfig } from 'vite'\n"
            "import react from '@vitejs/plugin-react'\n\n"
            "export default defineConfig({\n"
            "  plugins: [react()],\n"
            "})\n"
        ),
        "tailwind.config.js": (
            "/** @type {import('tailwindcss').Config} */\n"
            "export default {\n"
            "  content: [\n"
            "    './index.html',\n"
            "    './src/**/*.{js,ts,jsx,tsx}',\n"
            "  ],\n"
            "  theme: { extend: {} },\n"
            "  plugins: [],\n"
            "}\n"
        ),
        "postcss.config.js": (
            "export default {\n"
            "  plugins: {\n"
            "    tailwindcss: {},\n"
            "    autoprefixer: {},\n"
            "  },\n"
            "}\n"
        ),
        "index.html": (
            "<!doctype html>\n"
            "<html lang='en'>\n"
            "  <head>\n"
            "    <meta charset='UTF-8' />\n"
            "    <meta name='viewport' content='width=device-width, initial-scale=1.0' />\n"
            "    <title>FrontForge App</title>\n"
            "  </head>\n"
            "  <body>\n"
            "    <div id='root'></div>\n"
            "    <script type='module' src='/src/main.jsx'></script>\n"
            "  </body>\n"
            "</html>\n"
        ),
        "src/main.jsx": (
            "import React from 'react'\n"
            "import ReactDOM from 'react-dom/client'\n"
            "import App from './App'\n"
            "import './index.css'\n\n"
            "ReactDOM.createRoot(document.getElementById('root')).render(\n"
            "  <React.StrictMode>\n"
            "    <App />\n"
            "  </React.StrictMode>,\n"
            ")\n"
        ),
        "src/index.css": (
            "@tailwind base;\n"
            "@tailwind components;\n"
            "@tailwind utilities;\n"
        ),
    }
    
    for filename, content in defaults.items():
        path = OUTPUT_DIR / filename
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            print(f"  Added missing file: {filename}")

def npm_install():
    print("Running npm install...")
    
    result = subprocess.run(
        "npm install",
        cwd=OUTPUT_DIR,
        capture_output=True,
        text=True,
        shell=True
    )
    
    if result.returncode != 0:
        print("ERROR: npm install failed")
        print(result.stderr[:500])
        return False
    
    print("npm install successful")
    return True

def npm_build():
    print("Running npm run build...")
    
    result = subprocess.run(
        "npm run build",
        cwd=OUTPUT_DIR,
        capture_output=True,
        text=True,
        shell=True
    )
    
    if result.returncode == 0:
        print("Build successful!")
        return True, ""
    
    error_output = result.stdout + "\n" + result.stderr
    print("Build failed. Errors:")
    print(error_output[:1000])
    return False, error_output

def fix_prompt(original_prompt, error_output, attempt):
    return f"""The React app you generated has build errors. Fix attempt {attempt} of {MAX_RETRIES}.

ORIGINAL REQUEST:
{original_prompt}

BUILD ERRORS:
{error_output[:2000]}

INSTRUCTIONS:
- Return the COMPLETE corrected project JSON
- Fix every error shown above
- Do NOT change the app design or functionality
- Output ONLY valid JSON, nothing else
"""

def run_agent():
    print("\n== FrontForge AI - Single Agent ==\n")
    
    user_prompt = input("Describe the React app you want to build:\n> ")
    system_prompt = load_system_prompt()
    current_prompt = user_prompt
    
    for attempt in range(1, MAX_RETRIES + 2):
        if attempt == 1:
            print("\nGenerating your app...")
        else:
            print(f"\nFix attempt {attempt - 1} of {MAX_RETRIES}...")
        
        raw = call_ollama(current_prompt, system_prompt)
        
        try:
            data = parse_response(raw)
        except Exception as e:
            print(f"Parse error: {e}")
            if attempt <= MAX_RETRIES:
                current_prompt = fix_prompt(user_prompt, str(e), attempt)
                continue
            else:
                print("Max retries reached. Exiting.")
                exit(1)
        
        write_files(data)
        write_package_json(data)
        ensure_config_files()
        
        if not npm_install():
            exit(1)
        
        build_ok, error_output = npm_build()
        
        if build_ok:
            break
        
        if attempt <= MAX_RETRIES:
            current_prompt = fix_prompt(user_prompt, error_output, attempt)
        else:
            print("Build failed after all retries.")
            exit(1)
    
    print("\n== Generation Complete! ==")
    print(f"Your app is in: {OUTPUT_DIR}/")
    print(f"To preview: cd {OUTPUT_DIR} && npm run dev")


run_agent()