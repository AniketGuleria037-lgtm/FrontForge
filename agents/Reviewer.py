import sys
import os
sys.path.append(".")
from utils import call_ollama, parse_response
from pathlib import Path

def reviewer_agent(state):
    system_prompt=Path("prompts/review.txt").read_text(encoding="utf-8")
    user_prompt = user_prompt = f"""You are reviewing React code. Find ALL errors and fix them.

    I have found these errors already — make sure you fix them:
    1. Some components use class= instead of className=
    2. Some components are missing export default at the end

    Here are the files to review and fix:

    {state['style']}

    Return a JSON object with:
    - "passed": false if any errors found, true if none
    - "issues": list of all errors found
    - "fixed_files": ALL files with errors corrected

    Remember: Output ONLY the JSON object. Start with {{ and end with }}"""
    print("State style:", state['style'])

    raw=call_ollama(user_prompt, system_prompt)
    response=parse_response(raw)
    state["review"]=response
    return state

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
