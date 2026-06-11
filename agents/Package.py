import sys
import os
sys.path.append(".")
from utils import call_ollama, parse_response
from pathlib import Path

def package_agent(state):
    system_prompt=Path("prompts/package.txt").read_text(encoding="utf-8")
    user_prompt = f"""Based on this project plan, determine the required npm 
    dependencies and executes installation commands in an isolated environment.

    Project plan:
    {state['plan']}

    Remember: Output ONLY the JSON object. Start with {{ and end with }}"""

    raw=call_ollama(user_prompt, system_prompt)
    response=parse_response(raw)
    state["package"]=response
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
        "ui_architecture": None,
        "components": None,
        "style": None,
        "package": None,
        "review": None
    }
    result = package_agent(test_state)
    print(result["package"])  