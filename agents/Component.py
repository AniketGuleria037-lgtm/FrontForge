import sys
import os
sys.path.append(".")
from utils import call_ollama, parse_response
from pathlib import Path
from rag.retriever import retrieve

def component_agent(state):
    system_prompt=Path("prompts/components.txt").read_text(encoding="utf-8")
    docs = retrieve("React components Tailwind CSS hooks")
    user_prompt = f"""You must write the complete React JSX code for every file listed below.

    For each file, generate the FULL working React component code.
    Do NOT just describe the file. Write the actual code.

    Files to generate:
    {state['ui_architecture']}

    Relevant React and Tailwind documentation:
    {docs}

    Output a JSON object where each file has:
    - "path": the file path
    - "content": the COMPLETE JSX code for that file

    Remember: Output ONLY the JSON object. Start with {{ and end with }}"""

    raw=call_ollama(user_prompt, system_prompt)
    response=parse_response(raw)
    state["components"]=response
    return state

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
