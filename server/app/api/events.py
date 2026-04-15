from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from server.app.db.connection import get_db
from server.app.db import crud
from server.app.db.models import Event

router = APIRouter(
    prefix="/events",
    tags=["Events"],
)


@router.get("/")
async def list_events(
    jurisdiction_slug: str = Query(..., description="e.g. 'sacramento'"),
    body_name: str | None = Query(
        default=None, description="Filter by body name e.g. 'City Council'"
    ),
    db: AsyncSession = Depends(get_db),
):
    jurisdiction = await crud.get_jurisdiction_by_slug(db, jurisdiction_slug)
    if not jurisdiction:
        raise HTTPException(
            status_code=404, detail=f"Jurisdiction '{jurisdiction_slug}' not found."
        )

    stmt = (
        select(Event)
        .where(Event.jurisdiction_id == jurisdiction.id)
        .options(selectinload(Event.agenda_items))
    )

    if body_name:
        stmt = stmt.where(Event.body_name.ilike(f"%{body_name}%"))

    stmt = stmt.order_by(Event.event_date.desc())
    results = await db.execute(stmt)
    events = results.scalars().all()

    return [
        {
            "id": e.id,
            "legistar_event_id": e.legistar_event_id,
            "body_name": e.body_name,
            "event_date": e.event_date,
            "agenda_item_count": len(e.agenda_items),
        }
        for e in events
    ]


@router.get("/{event_id}")
async def get_event(event_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalars().first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")

    return {
        "id": event.id,
        "legistar_event_id": event.legistar_event_id,
        "jurisdiction_slug": event.jurisdiction.slug,
        "body_name": event.body_name,
        "event_date": event.event_date,
        "agenda_items": [
            {
                "id": item.id,
                "legistar_matter_id": item.legistar_matter_id,
                "matter_type": item.matter_type,
                "title": item.title,
                "has_summary": item.summary_report is not None,
            }
            for item in event.agenda_items
        ],
    }
