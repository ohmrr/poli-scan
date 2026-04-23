from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from server.app.db import crud
from server.app.db.connection import get_db
from server.app.db.models import Official
from server.app.schemas.official import OfficialResponse

router = APIRouter(
    prefix="/officials",
    tags=["Officials"],
)


def official_query():
    return select(Official).options(
        selectinload(Official.jurisdiction), selectinload(Official.holdings)
    )


def official_query():
    return select(Official).options(
        selectinload(Official.jurisdiction), selectinload(Official.holdings)
    )


@router.get("/search", response_model=list[OfficialResponse])
async def search_officials(
    name: str,
    jurisdiction_slug: str | None = Query(
        default=None, description="Filter by jurisdiction slug, e.g. 'sonoma-county'"
    ),
    db: AsyncSession = Depends(get_db),
):
    stmt = official_query().where(
        func.concat(Official.first_name, " ", Official.last_name).ilike(f"%{name}%")
    )

    if jurisdiction_slug:
        jurisdiction = await crud.get_jurisdiction_by_slug(db, jurisdiction_slug)
        if not jurisdiction:
            raise HTTPException(
                status_code=404,
                detail=f"Jurisdiction '{jurisdiction_slug}' not found.",
            )
        stmt = stmt.where(Official.jurisdiction_id == jurisdiction.id)

    stmt = stmt.order_by(Official.last_name, Official.first_name)
    return await db.scalars(stmt)


@router.get("/{official_id}", response_model=OfficialResponse)
async def get_official(official_id: int, db: AsyncSession = Depends(get_db)):
    official = await db.scalar(official_query().where(Official.id == official_id))
    if not official:
        raise HTTPException(
            status_code=404, detail=f"Official with id '{official_id}' not found."
        )
    return official
