import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from server.app.db.crud import get_agenda_items_by_jurisdiction_and_year
from server.app.db.models import Official

from .llm_providers import ollama_llm
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
    official_dict = {
        "full_name": official.full_name,
        "position": official.position,
        "holdings": holdings_list,
    }

    agenda_items = await get_agenda_items_by_jurisdiction_and_year(
        db, official.jurisdiction_id, year
    )
    item_dicts = [
        {
            "title": item.title,
            "attachments": [
                {"name": att.name, "url": att.url} for att in item.attachment_items
            ],
        }
        for item in agenda_items
    ]

    matches = []
    for item_dict in item_dicts:
        result = await check_conflict(official_dict, item_dict, ollama_llm, _sem)

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
