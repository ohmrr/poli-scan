import json
from typing import Callable
from .prompts import get_prompt
from .matching_utils import fetch_attachment_text
import asyncio

_sem = asyncio.Semaphore(5)


async def _process_attachment(
    official: dict, agenda_item: dict, att: dict, llm_fn: Callable
) -> dict | None:
    async with _sem:
        text = await fetch_attachment_text(att.get("url", ""))
        prompt = get_prompt(official, agenda_item, att.get("name", ""), text)
        response = await llm_fn(prompt)
        try:
            result = json.loads(response)
            if result.get("flagged"):
                return result
        except json.JSONDecodeError:
            print(f"LLM response was not valid JSON: {response}")
        return None


async def check_conflict(
    official: dict, agenda_item: dict, llm_fn: Callable
) -> dict | None:
    attachments = agenda_item.get("attachments", [])
    if not attachments:
        return None

    results = await asyncio.gather(
        *[
            _process_attachment(official, agenda_item, att, llm_fn)
            for att in attachments
        ]
    )

    return next((r for r in results if r is not None), None)
