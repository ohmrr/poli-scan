import httpx
import time

async def ollama_llm(prompt: str) -> str:
    start = time.time()  # start timer 
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://172.28.96.1:11434/api/generate",
                json={
                    "model": "qwen2.5:14b",
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                    "options": {
                        "num_ctx": 16384
                        }
                    },
                timeout=60.0
            )
            data = response.json()
            end = time.time()  # stop timer
            print(f"LLM took {end - start:.2f} seconds")  # print difference
            return data["response"]
    except httpx.RequestError as e:
        print(f"Ollama is not available: {e}")
        return ""  
    except Exception as e:
        print(f"Error Ollama LLM: {e}")
        return ""