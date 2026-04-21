import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from server.app.db.crud import get_agenda_items_by_jurisdiction_and_year, get_aye_voters
from server.app.db.models import Official

from .llm_providers import ollama_llm, groq_llm
from server.app.config import settings
from .matcher import check_conflict

_sem = asyncio.Semaphore(2)


async def run_matching_engine_for_official(
    db: AsyncSession, official_id: int, jurisdiction_slug: str
):
    result = await db.execute(
        select(Official)
        .where(Official.id == official_id)
        .options(selectinload(Official.holdings))
    )
    official = result.scalars().first()

    if not official:
        return {"Error": "Official not found/invalid official_id"}

    year = 2019
    holdings_list = [
        {"entity_name": h.entity_name, "year": h.year}
        for h in official.holdings
        if h.year == year
    ]
    if not holdings_list:
        return {"official_id": official.id, "official_name": official.full_name, "matches_found": 0, "matches": []}
    official_dict = {
        "full_name": official.full_name,
        "position": official.position,
        "holdings": holdings_list,
    }

    matches = []

    agenda_items = await get_agenda_items_by_jurisdiction_and_year(
        db, official.jurisdiction_id, year
    )
    llm_fn = groq_llm if settings.LLM_PROVIDER == "groq" else ollama_llm
    for agenda_item in agenda_items:
        aye_voters = await get_aye_voters(db, agenda_item.id)
        if aye_voters and official.id not in aye_voters:
            continue
        item_dict = {
            "title": agenda_item.title,
            "attachments": [
                {"name": att.name, "url": att.url} for att in agenda_item.attachment_items
            ],
        }
        
        result = await check_conflict(official_dict, item_dict, llm_fn, _sem)

        if result is not None:
            matches.append(result)

    return {
        "official_id": official.id,
        "official_name": official.full_name,
        "jurisdiction_slug": jurisdiction_slug,
        "holdings_count": len(official.holdings),
        "matches_found": len(matches),
        "matches": matches,
    }
