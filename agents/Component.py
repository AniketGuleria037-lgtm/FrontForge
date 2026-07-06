import sys
import os
sys.path.append(".")
from utils import call_ollama, parse_response
from pathlib import Path
from rag.retriever import retrieve

def component_agent(state):
    print("✓ COMPONENT AGENT STARTED")
    
    system_prompt = Path("prompts/components.txt").read_text(encoding="utf-8")
    files = state["ui_architecture"]["files"]
    generated_files = []

    for file in files:
        print(f"  Generating: {file['path']}")
        
        docs = retrieve("React functional component useState Tailwind CSS flexbox grid navbar hero card")
        
        user_prompt = f"""Generate the complete React JSX code for this single file only.

        File to generate:
        - Path: {file['path']}
        - Description: {file['description']}

        Project context:
        - Pages: {[f.get('path', '') for f in files if 'pages' in f.get('path', '')]}
        - Components: {[f.get('path', '') for f in files if 'components' in f.get('path', '')]}

        Relevant docs:
        {docs[:500]}

        Return JSON with exactly this structure:
        {{"files": [{{"path": "{file['path']}", "content": "complete jsx code here"}}]}}
        - Always include hardcoded sample data inside the component itself
        - Never rely on parent to pass props without defaults
        - If mapping over data, define the data array inside the component
        Output ONLY the JSON object."""

        raw = call_ollama(user_prompt, system_prompt)
        response = parse_response(raw)
        
        if response and response.get("files"):
            generated_files.extend(response["files"])
            print(f"  ✓ Generated: {file['path']}")
        else:
            print(f"  ✗ Failed: {file['path']}")

    return {"components": {"files": generated_files}}

if __name__ == "__main__":
    test_state = {
        "user_prompt": "Build a coffee shop app",
        "specs": {},
        "plan": {
            "pages": [
                {"name": "Home", "description": "Landing page"},
                {"name": "Menu", "description": "Menu page"}
            ],
            "components": [
                {"name": "Navbar", "description": "Navigation bar"},
                {"name": "Footer", "description": "Footer"}
            ],
            "dependencies": ["react", "tailwindcss"]
        },
        "ui_architecture": {
        "files": [
            {"path": "src/App.jsx", "description": "Main app"},
            {"path": "src/components/Navbar.jsx", "description": "Navbar"},
            {"path": "src/pages/Home.jsx", "description": "Home page"}
        ]
    },
        "components": None,
        "style": None,
        "package": None,
        "review": None
    }
    result = component_agent(test_state)
    print(result["components"])
