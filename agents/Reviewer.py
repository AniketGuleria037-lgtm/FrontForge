import sys
import os
sys.path.append(".")
from utils import call_ollama, parse_response
from pathlib import Path

def reviewer_agent(state):
    print("✓ REVIEWER AGENT STARTED")

    if not state.get("style"):
        print("WARNING: Style is None")
        return {"review": {"passed": False, "issues": [], "fixed_files": []}}

    files = state["style"]["files"]
    fixed_files = []

    for file in files:
        print(f"  Reviewing: {file['path']}")
        content = file["content"]
        
        # Fix common errors directly in Python — no LLM needed
        fixed_content = content
        
        # Fix 1: class= → className=
        fixed_content = fixed_content.replace(' class=', ' className=')
        
        # Fix 2: ensure default export exists
        if 'export default' not in fixed_content:
            name = Path(file['path']).stem
            fixed_content += f'\n\nexport default {name};'
        
        if fixed_content != content:
            print(f"  ✓ Fixed issues in: {file['path']}")
        else:
            print(f"  ✓ No issues: {file['path']}")
            
        fixed_files.append({
            "path": file["path"],
            "content": fixed_content
        })

    return {"review": {"passed": True, "issues": [], "fixed_files": fixed_files}}

if __name__ == "__main__":
    test_state = {
    "user_prompt": "Build a coffee shop app",
    "specs": {},
    "plan": {},
    "ui_architecture": {},
    "components": {},
    "style": {
        "files": [
            {
                "path": "src/App.jsx",
                "content": "import React from 'react';\nimport Navbar from './components/Navbar';\n\nfunction App() {\n  return (\n    <div class='min-h-screen'>\n      <Navbar />\n    </div>\n  );\n}\n\nexport default App;"
            },
            {
                "path": "src/components/Navbar.jsx",
                "content": "import React from 'react';\n\nconst Navbar = () => {\n  return (\n    <nav class='bg-white p-4'>\n      <h1 class='text-2xl font-bold'>Coffee Shop</h1>\n    </nav>\n  );\n};\n\nexport default Navbar;"
            },
            {
                "path": "src/pages/Home.jsx",
                "content": "import React from 'react';\n\nconst Home = () => {\n  return (\n    <div class='p-8'>\n      <h1 class='text-3xl font-bold'>Welcome</h1>\n    </div>\n  );\n};"
            }
        ]
    },
    "package": None,
    "review": None
}
    result=reviewer_agent(test_state)
    print(result["review"])
