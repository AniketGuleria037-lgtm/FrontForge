import sys
import os
sys.path.append(".")
from utils import call_ollama, parse_response
from pathlib import Path

def clarification_agent(state):
    print(state["user_prompt"])
    framework = input("What framework? (React/Next.js) [default: React]: ").strip()
    if framework == "":
        framework = "React"
    styling = input("What styling? (Tailwind/Bootstrap) [default: Tailwind]: ").strip()
    if styling == "":
        styling = "Tailwind"
    theme = input("What theme? (light/dark) [default: light]: ").strip()
    if theme == "":
        theme = "Light"
    system_prompt=Path("prompts/clarification.txt").read_text(encoding="utf-8")
    user_prompt = f"""The user wants to build: "{state['user_prompt']}"

    Framework preference: {framework}
    Styling preference: {styling}  
    Theme preference: {theme}

    Based on the app description, infer:
    - What specific pages this app needs
    - What the app is actually about
    - The complexity level

    Remember: Output ONLY the JSON object."""

    raw=call_ollama(user_prompt, system_prompt)
    response=parse_response(raw)

    return {"specs": response}

if __name__ == "__main__":
    test_state = {
        "user_prompt": "Build a coffee shop app",
        "specs": None,
        "plan": None,
        "ui_architecture": None,
        "components": None,
        "style": None,
        "package": None,
        "review": None
    }
    result = clarification_agent(test_state)
    print(result["specs"])

    