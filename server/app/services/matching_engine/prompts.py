
def get_prompt(official: dict, agenda_item: dict,attachment_name :str = "",attachment_text: str = "") -> str:
    name = official.get("full_name", "Unknown Official")
    position = official.get("position", "Unknown Position")
    holdings = official.get("holdings", [])
    holdings_names = ", ".join([h["entity_name"] for h in holdings])
    spousal_income = official.get("spousal_income", [])
    title = agenda_item.get("title", "No Title")
    return f"""
    You are a government ethics compliance/analyst officer.
    Official Name: {name} ({position})
    Holdings: {holdings_names}
    Agenda Title: {title}
    Agenda Attachment Name: {attachment_name}
    Agenda Attachment Text: {attachment_text}
    Does this official have a potential conflict of interest with this agenda item based on their holdings?
    reply in JSON only, no extra text:
    {{
    "flagged": true or false,
    "confidence": an integer from 0 to 100 representing your confidence that a conflict exists (0 = no conflict at all, 100 = certain conflict),
    "matched_interest": "the holding that matched or null",
    "official_name": "their name",
    "agenda_title": "the title",
    "reasoning": "one sentence explanation"
    }}
    """