import requests

response = requests.post("http://localhost:11434/api/generate", json={
    "model": "qwen3:4b",
    "prompt": "Write a React component that shows Hello World",
    "stream": False,
    "think": False
})

data = response.json()
print(data["response"])