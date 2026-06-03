import os
import json
import re
import subprocess
import shutil
import requests
from pathlib import Path

# ── Configuration ──────────────────────────────────────
OLLAMA_URL         = "http://localhost:11434/api/generate"
MODEL              = "qwen2.5-coder:3b"
OUTPUT_DIR         = Path("generated-app")
SYSTEM_PROMPT_FILE = Path("prompts/system_prompt.txt")
MAX_RETRIES        = 3