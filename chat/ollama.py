import os
import httpx

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "127.0.0.1:11434")
OLLAMA_URL = f"http://{OLLAMA_HOST}/api/chat"
MODEL = "gemma3"


async def stream_response(messages):
    """Async generator that streams response lines from Ollama.

    Yields decoded text chunks (one line per yield).
    """
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": True,
    }

    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("POST", OLLAMA_URL, json=payload) as r:
            r.raise_for_status()
            async for line in r.aiter_lines():
                if line:
                    yield line
