import logging
import time
from openai import AsyncOpenAI
import httpx

from server.app.config import settings

logger = logging.getLogger(__name__)
_client = httpx.AsyncClient(timeout=60.0)


async def ollama_llm(prompt: str) -> str:
    start = time.time()

    try:
        response = await _client.post(
            f"{settings.OLLAMA_BASE_URL.strip()}/api/generate",
            json={
                "model": settings.OLLAMA_MODEL.strip(),
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
        raw = response.text[:500] if response is not None else "(no response)"
        logger.error("Ollama error: %s | Raw response: %s", e, raw)
        return ""


_groq_client = AsyncOpenAI(
    api_key=settings.GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)
async def groq_llm(prompt: str) -> str:
    try:
        response = await _groq_client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error("Groq error: %s", e)
        return ""


async def close():
    await _client.aclose()
    await _groq_client.close()