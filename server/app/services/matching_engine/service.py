import asyncio
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from server.app.db.crud import get_agenda_items_by_jurisdiction_and_year, get_aye_voters, save_match_result, is_item_checked, mark_item_checked, get_matches_by_official
from server.app.db.models import Official

from .llm_providers import ollama_llm, groq_llm
from server.app.config import settings
from .matcher import check_conflict

logger = logging.getLogger(__name__)

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
    total = len(agenda_items)
    for i, agenda_item in enumerate(agenda_items, 1):
        aye_voters = await get_aye_voters(db, agenda_item.id)
        if aye_voters and official.id not in aye_voters:
            continue
        if await is_item_checked(db, official.id, agenda_item.id):
            logger.info("[%d/%d] Skipping item %d (matter %s) — already checked", i, total, agenda_item.id, agenda_item.legistar_matter_id)
            continue

        logger.info("[%d/%d] Checking agenda item %d (matter %s): %s", i, total, agenda_item.id, agenda_item.legistar_matter_id, (agenda_item.title or "")[:60])
        item_dict = {
            "title": agenda_item.title,
            "attachments": [
                {"name": att.name, "url": att.url} for att in agenda_item.attachment_items
            ],
        }

        result = await check_conflict(official_dict, item_dict, llm_fn, _sem)

        if result is not None:
            matches.append(result)
            await save_match_result(
                db,
                official_id=official.id,
                jurisdiction_id=official.jurisdiction_id,
                agenda_item_id=agenda_item.id,
                matched_interest=result.get("matched_interest") or "unknown",
                confidence=result.get("confidence", 0),
                flagged=result.get("flagged", True),
                reason=result.get("reasoning"),
                pdf_url=result.get("pdf_url"),
                attachment_name=result.get("attachment_name"),
                event_date=agenda_item.event.event_date if agenda_item.event else None,
                year=year,
            )

        await mark_item_checked(
            db,
            official_id=official.id,
            agenda_item_id=agenda_item.id,
            found_match=result is not None,
        )

    stored = await get_matches_by_official(db, official.id)
    all_matches = matches + [
        {
            "flagged": m.flagged,
            "confidence": m.confidence,
            "matched_interest": m.matched_interest,
            "reasoning": m.reason,
            "pdf_url": m.pdf_url,
            "attachment_name": m.attachment_name,
        }
        for m in stored
        if not any(
            x.get("matched_interest") == m.matched_interest and x.get("pdf_url") == m.pdf_url
            for x in matches
        )
    ]

    return {
        "official_id": official.id,
        "official_name": official.full_name,
        "jurisdiction_slug": jurisdiction_slug,
        "holdings_count": len(official.holdings),
        "matches_found": len(all_matches),
        "matches": all_matches,
    }
