import sys
import json
import shutil
import subprocess
sys.path.append(".")
from pathlib import Path
from pipeline import build_pipeline

OUTPUT_DIR = Path("generated-app")

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

def fix_imports():
    import re
    app_path = OUTPUT_DIR / "src" / "App.jsx"
    if not app_path.exists():
        return

    content = app_path.read_text(encoding="utf-8")
    
    # Fix spaces in import paths
    content = re.sub(r"from '(\.\/[^']*)\s+([^']*)'", r"from '\1\2'", content)
    
    # Get all local imports
    imports = re.findall(r"from '(\./[^']+)'", content)
    
    for imp in imports:
        clean_imp = imp.strip()
        file_path = OUTPUT_DIR / "src" / clean_imp.replace("./", "")
        
        # Add .jsx if no extension
        if not file_path.suffix:
            file_path = Path(str(file_path) + ".jsx")
        
        # Create missing files
        if not file_path.exists():
            print(f"  Creating missing: {file_path.name}")
            file_path.parent.mkdir(parents=True, exist_ok=True)
            name = file_path.stem.strip()
            file_path.write_text(
                f"import React from 'react'\n\n"
                f"export default function {name}() {{\n"
                f"  return (\n"
                f"    <div className='p-8 text-center'>\n"
                f"      <h2 className='text-2xl font-bold'>{name}</h2>\n"
                f"    </div>\n"
                f"  )\n"
                f"}}\n"
            )
    
    # Write fixed App.jsx back
    app_path.write_text(content, encoding="utf-8")
    print("Import paths fixed")

def run_pipeline():
    print("\n== FrontForge AI - Multi Agent ==\n")
    user_prompt = input("Describe the React app you want to build:\n> ")
    
    initial_state = {
        "user_prompt": user_prompt,
        "specs": None,
        "plan": None,
        "ui_architecture": None,
        "components": None,
        "style": None,
        "package": None,
        "review": None
    }
    
    pipeline = build_pipeline()
    print("\nRunning pipeline...\n")
    final_state = pipeline.invoke(initial_state)
    review = final_state["review"]
    style = final_state["style"]

# Use fixed_files from reviewer if available and complete
# Otherwise fall back to styled files
    if review and review.get("fixed_files") and len(review["fixed_files"]) > 2:
        files_data = {"files": review["fixed_files"]}
        print(f"Using Reviewer files: {len(review['fixed_files'])} files")
    else:
        files_data = {"files": style["files"]}
        print(f"Using Styling files: {len(style['files'])} files")

    package_data = final_state["package"]
    write_files(files_data)
    write_package_json(package_data)
    ensure_config_files()
    fix_imports()
    
    if not npm_install():
        exit(1)
    
    build_ok, error = npm_build()
    
    if build_ok:
        print("\n== Generation Complete! ==")
        print(f"cd generated-app && npm run dev")
    else:
        print("Build failed:", error[:500])

run_pipeline()