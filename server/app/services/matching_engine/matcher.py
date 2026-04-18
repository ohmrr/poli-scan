import asyncio
import json
import logging
from typing import Callable

from .matching_utils import fetch_attachment_text
from .prompts import get_prompt

logger = logging.getLogger(__name__)


async def _process_attachment(
    official: dict,
    agenda_item: dict,
    att: dict,
    llm_fn: Callable,
    sem: asyncio.Semaphore,
) -> dict | None:
    async with sem:
        text = await fetch_attachment_text(att.get("url", ""))
        prompt = get_prompt(official, agenda_item, att.get("name", ""), text)

        response = await llm_fn(prompt)

        if not response:
            logger.warning("Skipping attachment '%s', empty LM response", att.get('name'))

        try:
            result = json.loads(response)

            if result.get("flagged"):
                return result
        except json.JSONDecodeError:
            logger.log("Bad JSON from LLM for attachment '%s': %s", att.get('name'), response[:200])
            
        return None


async def check_conflict(
    official: dict, agenda_item: dict, llm_fn: Callable, sem: asyncio.Semaphore
) -> dict | None:
    attachments = agenda_item.get("attachments", [])

    if not attachments:
        return None

    results = await asyncio.gather(
        *[
            _process_attachment(official, agenda_item, att, llm_fn, sem)
            for att in attachments
        ]
    )

    return next((r for r in results if r is not None), None)
