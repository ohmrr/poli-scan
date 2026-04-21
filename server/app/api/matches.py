from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from server.app.db import crud
from server.app.db.connection import get_db
from server.app.db.models import MatchResult, Jurisdiction

router = APIRouter(
    prefix="/matches",
    tags=["Matches"],
)


@router.get("/official/{official_id}")
async def get_matches_for_official(
    official_id: int,
    db: AsyncSession = Depends(get_db),
):
    matches = await crud.get_matches_by_official(db, official_id)

    return [
        {
            "id": m.id,
            "official_id": m.official_id,
            "jurisdiction_id": m.jurisdiction_id,
            "agenda_item_id": m.agenda_item_id,
            "matched_interest": m.matched_interest,
            "confidence": m.confidence,
            "flagged": m.flagged,
            "reason": m.reason,
            "pdf_url": m.pdf_url,
            "attachment_name": m.attachment_name,
            "event_date": m.event_date,
            "year": m.year,
            "created_at": m.created_at
        }
        for m in matches
    ]


@router.get("/{jurisdiction_slug}")
async def get_matches_by_jurisdiction(
    jurisdiction_slug: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MatchResult)
        .join(Jurisdiction, MatchResult.jurisdiction_id == Jurisdiction.id)
        .where(Jurisdiction.slug == jurisdiction_slug)
    )
    
    matches = result.scalars().all()

    return [
        {
            "id": m.id,
            "official_id": m.official_id,
            "jurisdiction_id": m.jurisdiction_id,
            "agenda_item_id": m.agenda_item_id,
            "matched_interest": m.matched_interest,
            "confidence": m.confidence,
            "flagged": m.flagged,
            "reason": m.reason,
            "pdf_url": m.pdf_url,
            "attachment_name": m.attachment_name,
            "event_date": m.event_date,
            "year": m.year,
            "created_at": m.created_at
        }
        for m in matches
    ]