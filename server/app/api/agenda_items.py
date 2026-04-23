from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from server.app.db import crud
from server.app.db.connection import get_db
from server.app.db.models import AgendaItem, Event, Jurisdiction
from server.app.schemas.agenda_item import (
    AgendaItemSummaryResponse,
    AgendaItemDetailResponse,
)

router = APIRouter(
    prefix="/agenda-items",
    tags=["Agenda Items"],
)


def agenda_item_query():
    return select(AgendaItem).options(
        selectinload(AgendaItem.event).selectinload(Event.jurisdiction)
    )


@router.get("/search", response_model=list[AgendaItemDetailResponse])
async def search_agenda_items(
    q: str = Query(..., description="Search term matched against title and summary"),
    jurisdiction_slug: str | None = Query(
        default=None, description="Narrow to a specific jurisdiction"
    ),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        agenda_item_query()
        .join(Event)
        .join(Jurisdiction)
        .where(AgendaItem.title.ilike(f"%{q}%"))
        .order_by(AgendaItem.id.desc())
        .limit(50)
    )
    if jurisdiction_slug:
        jurisdiction = await crud.get_jurisdiction_by_slug(db, jurisdiction_slug)
        if not jurisdiction:
            raise HTTPException(
                status_code=404, detail=f"Jurisdiction '{jurisdiction_slug}' not found."
            )
        stmt = stmt.where(Event.jurisdiction_id == jurisdiction.id)

    return await db.scalars(stmt)


@router.get("/{item_id}", response_model=AgendaItemDetailResponse)
async def get_agenda_item(item_id: int, db: AsyncSession = Depends(get_db)):
    item = await db.scalar(agenda_item_query().where(AgendaItem.id == item_id))
    if not item:
        raise HTTPException(status_code=404, detail="Agenda item not found.")
    return item
