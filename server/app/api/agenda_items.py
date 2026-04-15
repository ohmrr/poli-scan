from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from server.app.db.connection import get_db
from server.app.db.models import AgendaItem

from server.app.db import crud
from server.app.db.models import Event, Jurisdiction


router = APIRouter(
    prefix="/agenda-items",
    tags=["Agenda Items"],
)


@router.get("/search")
async def search_agenda_items(
    q: str = Query(..., description="Search term matched against title and summary"),
    jurisdiction_slug: str | None = Query(
        default=None, description="Narrow to a specific jurisdiction"
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Full text search across agenda item titles and summary reports.
    This is the core endpoint for finding agenda items that might relate
    to an official's stock holdings.
    """

    stmt = (
        select(AgendaItem)
        .join(Event)
        .join(Jurisdiction)
        .options(selectinload(AgendaItem.event).selectinload(Event.jurisdiction))
        .where(
            AgendaItem.title.ilike(f"%{q}%") | AgendaItem.summary_report.ilike(f"%{q}%")
        )
    )

    if jurisdiction_slug:
        jurisdiction = await crud.get_jurisdiction_by_slug(db, jurisdiction_slug)

        if not jurisdiction:
            raise HTTPException(
                status_code=404, detail=f"Jurisdiction '{jurisdiction_slug}' not found."
            )

        stmt = stmt.where(Event.jurisdiction_id == jurisdiction.id)

    stmt = stmt.order_by(AgendaItem.id.desc()).limit(50)
    result = await db.execute(stmt)
    items = result.scalars().all()

    return [
        {
            "id": item.id,
            "legistar_matter_id": item.legistar_matter_id,
            "matter_type": item.matter_type,
            "title": item.title,
            "has_summary": item.summary_report is not None,
            "event": {
                "id": item.event.id,
                "body_name": item.event.body_name,
                "event_date": item.event.event_date,
                "jurisdiction_slug": item.event.jurisdiction.slug,
            },
        }
        for item in items
    ]


@router.get("/{item_id}")
async def get_agenda_item(item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(AgendaItem)
        .where(AgendaItem.id == item_id)
        .options(selectinload(AgendaItem.event).selectinload(Event.jurisdiction))
    )
    item = result.scalars().first()

    if not item:
        raise HTTPException(status_code=404, detail="Agenda item not found.")

    return {
        "id": item.id,
        "legistar_matter_id": item.legistar_matter_id,
        "matter_type": item.matter_type,
        "title": item.title,
        "summary_report": item.summary_report,
        "event": {
            "id": item.event.id,
            "legistar_event_id": item.event.legistar_event_id,
            "body_name": item.event.body_name,
            "event_date": item.event.event_date,
            "jurisdiction_slug": item.event.jurisdiction.slug,
        },
    }
