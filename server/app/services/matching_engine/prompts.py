def get_prompt(official: dict, agenda_item: dict) -> str:
    name = official.get("full_name", "Unknown Official")
    position = official.get("position", "Unknown Position")
    holdings = official.get("holdings", [])
    holdings_names = ", ".join([h["entity_name"] for h in holdings])
    title = agenda_item.get("EventItemTitle", "No Title")
    summary = agenda_item.get("EventItemSummary", "No Summary")
    summary_snippet = summary[:500]
    return f"""
    You are a goverment ethics compliance/analyst officer.
    Official Name: {name} ({position})
    Holdings: {holdings_names}
    Agenda Title: {title}
    Agenda Summary Snippet: {summary_snippet}
    Does this official have a potential conflict of interest with this agenda item based on their holdings?
    reply in JSON only, no extra text:
    {{
    "flagged": true or false,
    "confidence": "high", "medium", or "low",
    "matched_interest": "the holding that matched or null",
    "official_name": "their name",
    "agenda_title": "the title",
    "reasoning": "one sentence explanation"
    }}
    """