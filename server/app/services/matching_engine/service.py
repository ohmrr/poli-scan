from server.app.db.models import Official
from .matcher import check_conflict
from server.app.db.crud import get_agenda_items_by_jurisdiction_and_year
from .llm_providers import ollama_llm
"""
Bridge database data to the matching engine.
This file should:
1. load an official and their holdings from the database
2. find candidate agenda items from the database
3. map database fields into matcher input format
4. run the matcher on each candidate item
5. return flagged matches
"""

#testing matching engine service
async def run_matching_engine_for_offical(db,official_id: int, jurisdiction_slug: str): 
    official = db.query(Official).filter(Official.id == official_id).first()
    if not official:
        return {"Error": "Official not found/invalid official_id"}
    year = 2019
    matches = []
    holdings_list = []
    for h in official.holdings:
        if h.year == year:
            holdings_list.append({
                "entity_name": h.entity_name,
                "year": h.year
            })

    official_dict = {
        "full_name": official.full_name,
        "position": official.position,
        "holdings": holdings_list,
    }

    agenda_items = get_agenda_items_by_jurisdiction_and_year(
        db, official.jurisdiction_id, year
    )

    for item in agenda_items:
        att_list = []
        for att in item.attachment_items:
            att_list.append({
                "name": att.name,
                "url": att.url
            })
        item_dict = {
            "title": item.title,
            "attachments": att_list
        }
        result = await check_conflict(official_dict, item_dict,ollama_llm)
        if result:
            matches.append(result)
    return {
        "official_id": official.id,
        "official_name": f"{official.first_name or ''} {official.last_name or ''}".strip(),
        "jurisdiction_slug": jurisdiction_slug,
        "holdings_count": len(official.holdings),
        "matches_found": len(matches),
        "matches": matches,
    }