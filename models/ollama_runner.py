import requests
from requests.adapters import HTTPAdapter, Retry

session = requests.Session()
session.mount("http://", HTTPAdapter(max_retries=3))


def ask_ollama(prompt, model="mistral:7b-instruct-q4_0") -> str:
    response = session.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
        },
        timeout=180,
    )
    if response.ok:
        return response.json()["response"].strip()
    else:
        raise RuntimeError(f"Ollama error: {response.text}")
