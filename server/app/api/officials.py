from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from server.app.db import crud
from server.app.db.connection import get_db
from server.app.db.models import Official

router = APIRouter(
    prefix="/officials",
    tags=["Officials"],
)


@router.get("/search")
async def search_officials(
    name: str,
    jurisdiction_slug: str | None = Query(
        default=None, description="Filter by jurisdiction slug, e.g. 'sonoma-county'"
    ),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Official)
        .where(
            func.concat(Official.first_name, " ", Official.last_name).ilike(f"%{name}%")
        )
        .options(selectinload(Official.jurisdiction), selectinload(Official.holdings))
    )

    if jurisdiction_slug:
        jurisdiction = await crud.get_jurisdiction_by_slug(db, jurisdiction_slug)
        if not jurisdiction:
            raise HTTPException(
                status_code=404,
                detail=f"Jurisdiction '{jurisdiction_slug}' not found.",
            )
        stmt = stmt.order_by(Official.last_name, Official.first_name)

    result = await db.execute(stmt)
    officials = result.scalars().all()

    return [
        {
            "id": o.id,
            "full_name": o.full_name,
            "jurisdiction_slug": o.jurisdiction.slug,
            "agency": o.agency,
            "holdings": [
                {"entity_name": h.entity_name, "year": h.year} for h in o.holdings
            ],
        }
        for o in officials
    ]


@router.get("/{official_id}")
async def get_official(official_id: int, db: AsyncSession = Depends(get_db)):
    official = await crud.get_official_by_id(db, official_id)

    if not official:
        raise HTTPException(
            status_code=404, detail=f"Official with id '{official_id}' not found."
        )

    return {
        "id": official.id,
        "full_name": official.full_name,
        "jurisdiction_id": official.jurisdiction_id,
        "jurisdiction_slug": official.jurisdiction.slug,
        "agency": official.agency,
        "position": official.position,
        "email": official.email,
        "legistar_person_id": official.legistar_person_id,
        "holdings": [
            {"entity_name": h.entity_name, "year": h.year} for h in official.holdings
        ],
    }
