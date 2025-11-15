"""
This file centralizes the entire llm call/response process.
The llms can be used:
 - locally via ollama (if installed)
 - remotely via:
    - google gemini (google-genai)
    - other...

the framework is set in .env
"""

from dotenv import load_dotenv
import os

PROVIDERS = {
    "ollama": _load_ollama
}

def _load_ollama():
    pass

def _select_provider():
    load_dotenv()
    provider = os.environ.get("PROVIDER")
    if provider not in 