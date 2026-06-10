import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath("agents/planner.py"))))
from utils import call_ollama, parse_response
from pathlib import Path
import state

def planner_agent(state):
    system_prompt=Path("prompts/planner.txt").read_text(encoding="utf-8")
    user_prompt = f"Create a project plan for this app: {state['specs']}"

    raw=call_ollama(user_prompt, system_prompt)
    response=parse_response(raw)
    state["plan"]=response
    return state

if __name__ == "__main__":
    test_state = {
        "user_prompt": "Build a coffee shop app",
        "specs": {
            "framework": "React",
            "styling": "Tailwind",
            "pages": ["Home", "Menu", "Contact"],
            "theme": "light",
            "complexity": "simple"
        },
        "plan": None,
        "ui_architecture": None,
        "components": None,
        "style": None,
        "package": None,
        "review": None
    }
    result = planner_agent(test_state)
    print(result["plan"])
