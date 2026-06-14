import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath("agents/planner.py"))))
from utils import call_ollama, parse_response
from pathlib import Path
import state

def planner_agent(state):
    print("✓ PLANNER AGENT STARTED")
    print("  Specs received:", state["specs"])
    system_prompt=Path("prompts/planner.txt").read_text(encoding="utf-8")
    user_prompt = f"""Create a detailed project plan for this SPECIFIC app:

    App description: "{state['user_prompt']}"
    Specs: {state['specs']}

    The pages and components must be SPECIFIC to this app.
    For a coffee shop: Menu page, About page, coffee product cards
    For a hospital: Patients page, Doctors page, appointment cards
    For a portfolio: Projects page, Skills page, contact form

    Output ONLY the JSON object."""

    raw=call_ollama(user_prompt, system_prompt)
    response=parse_response(raw)
    return {"plan": response}

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
