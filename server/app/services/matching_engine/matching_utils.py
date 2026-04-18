import asyncio
import io

import httpx
import pdfplumber

_client = httpx.AsyncClient(timeout=30.0)


def parse_pdf(pdf_bytes: bytes) -> str:
    parts = []

    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()

            if text:
                parts.append(text)

    return "\n".join(parts)


async def fetch_attachment_text(url: str) -> str:
    try:
        resp = await _client.get(url)
        resp.raise_for_status()

        return await asyncio.to_thread(parse_pdf, resp.content)
    except Exception:
        return ""


async def close():
    await _client.aclose()
