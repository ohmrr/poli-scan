from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from server.app.db import crud
from server.app.db.connection import get_db
from server.app.db.models import Event
from server.app.schemas.event import EventSummaryResponse, EventDetailResponse

router = APIRouter(
    prefix="/events",
    tags=["Events"],
)


def event_query():
    return select(Event).options(
        selectinload(Event.agenda_items),
        selectinload(Event.jurisdiction),
    )


@router.get("", response_model=list[EventSummaryResponse])
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
        event_query()
        .where(Event.jurisdiction_id == jurisdiction.id)
        .order_by(Event.event_date.desc())
    )
    if body_name:
        stmt = stmt.where(Event.body_name.ilike(f"%{body_name}%"))

    return await db.scalars(stmt)


@router.get("/{event_id}", response_model=EventDetailResponse)
async def get_event(event_id: int, db: AsyncSession = Depends(get_db)):
    event = await db.scalar(event_query().where(Event.id == event_id))
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")
    return event
