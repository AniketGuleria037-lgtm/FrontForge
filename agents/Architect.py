import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath("agents/planner.py"))))
from utils import call_ollama, parse_response
from pathlib import Path

def architect_agent(state):
    print("✓ ARCHITECT AGENT STARTED")
    print("  Plan received:", "OK" if state["plan"] else "NONE")
    system_prompt=Path("prompts/architect.txt").read_text(encoding="utf-8")
    user_prompt = f"""Based on this project plan, design the complete folder structure.
    Return a JSON object with a 'files' array. Each file must have 'path' and 'description'.

    Project plan:
    {state['plan']}

Remember: Output ONLY the JSON object. Start with {{ and end with }}"""

    raw=call_ollama(user_prompt, system_prompt)
    response=parse_response(raw)
    return {"ui_architecture": response}

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
    result = architect_agent(test_state)
    print(result["ui_architecture"])
