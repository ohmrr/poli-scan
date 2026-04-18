import logging
import time

import httpx

from server.app.config import settings

logger = logging.getLogger(__name__)
_client = httpx.AsyncClient(timeout=60.0)


async def ollama_llm(prompt: str) -> str:
    start = time.time()

    try:
        response = await _client.post(
            f"{settings.OLLAMA_BASE_URL}/api/generate",
            json={
                "model": settings.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {"num_ctx": 16384},
            },
        )

        data = response.json()
        logger.debug("LLM took %.2f seconds", time.time() - start)

        return data["response"]
    except httpx.RequestError as e:
        logger.error("Ollama unavailable: %s", e)
        return ""
    except Exception as e:
        logger.error("Ollama error: %s | Raw response: %s", e, response.text[:500])
        return ""


async def close():
    await _client.aclose()
