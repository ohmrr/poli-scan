import json
from typing import Callable
from llm_providers import ollama_llm
from .prompts import get_prompt
from .matching_utils import get_keywords, prefilter

async def check_conflict(official: dict, agenda_item: dict, llm_fn: Callable) -> dict | None:
    date_str = agenda_item.get("EventItemDate", "")
    if not date_str or len(date_str) < 4:
        return None
    year = int(agenda_item.get("EventItemDate", "")[:4])
    keywords = get_keywords(holdings=official.get("holdings",[]), year=year)
    if not prefilter(keywords, agenda_item):
        return None
    prompt = get_prompt(official, agenda_item)
    response = await llm_fn(prompt)
    try:
        result = json.loads(response)
        if result.get("flagged"):
            return result
    except json.JSONDecodeError:
        print(f"LLM response was not valid JSON: {response}")
    return None








