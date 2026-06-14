import sys
import os
sys.path.append(".")
from utils import call_ollama, parse_response
from pathlib import Path
from rag.retriever import retrieve

def styling_agent(state):
    print("✓ STYLING AGENT STARTED")
    print("  Components received:", "OK" if state["components"] else "NONE")
    
    system_prompt = Path("prompts/styling.txt").read_text(encoding="utf-8")
    files = state["components"]["files"]
    styled_files = []

    for file in files:
        print(f"  Styling: {file['path']}")
        
        user_prompt = f"""Improve the Tailwind CSS styling for this single React file.
Keep all existing functionality. Only enhance the visual design.

File to style:
Path: {file['path']}
Current code:
{file['content']}

Return JSON:
{{"files": [{{"path": "{file['path']}", "content": "improved code here"}}]}}

Output ONLY the JSON object."""

        raw = call_ollama(user_prompt, system_prompt)
        response = parse_response(raw)
        
        if response and response.get("files"):
            styled_files.extend(response["files"])
            print(f"  ✓ Styled: {file['path']}")
        else:
            styled_files.append(file)
            print(f"  ✗ Failed styling, keeping original: {file['path']}")

    return {"style": {"files": styled_files}}

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
        "components": {'files': [{'path': 'src/App.jsx', 'content': 'import React from \'react\';\nimport { BrowserRouter as Router, Routes, Route } from \'react-router-dom\';\nimport Home from \'./pages/Home\';\nimport Navbar from \'./components/Navbar\';\n\nfunction App() {\n  return (\n    <Router>\n      <div className="min-h-screen flex flex-col">\n        <Navbar />\n        <main className="flex-grow">\n          <Routes>\n            <Route path="/" element={<Home />} />\n          </Routes>\n        </main>\n      </div>\n    </Router>\n  );\n}\n\nexport default App;'}, {'path': 'src/components/Navbar.jsx', 'content': 'import React from \'react\';\n\nconst Navbar = () => {\n  return (\n    <nav className="bg-white shadow-md dark:bg-gray-800 p-4 fixed w-full z-50">\n      <div className="container mx-auto flex justify-between items-center">\n        <h1 className="text-2xl font-bold text-gray-800 dark:text-white">My App</h1>\n        <div className="flex space-x-4">\n          <a href="/" className="text-gray-700 dark:text-gray-200 hover:text-brand-500 transition-colors">Home</a>\n          <a href="/about" className="text-gray-700 dark:text-gray-200 hover:text-brand-500 transition-colors">About</a>\n        </div>\n      </div>\n    </nav>\n  );\n};\n\nexport default Navbar;'}, {'path': 'src/pages/Home.jsx', 'content': 'import React from \'react\';\n\nconst Home = () => {\n  return (\n    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-4">\n      <div className="container mx-auto max-w-4xl">\n        <h1 className="text-3xl font-bold text-gray-800 dark:text-white mb-4">Welcome to My App</h1>\n        <p className="text-gray-600 dark:text-gray-300 mb-6">\n          This is the home page of my React application with Tailwind CSS.\n        </p>\n        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">\n          <h2 className="text-2xl font-semibold text-gray-800 dark:text-white mb-2">About This App</h2>\n          <p className="text-gray-600 dark:text-gray-300">\n            This app demonstrates a simple React application with Tailwind CSS for styling.\n          </p>\n        </div>\n      </div>\n    </div>\n  );\n};\n\nexport default Home;'}]},
        "style": None,
        "package": None,
        "review": None
    }
    result = styling_agent(test_state)
    print(result["style"])