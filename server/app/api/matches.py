from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from server.app.db import crud
from server.app.db.connection import get_db
from server.app.db.models import MatchResult, Jurisdiction
from server.app.schemas.match import MatchResultResponse

router = APIRouter(
    prefix="/matches",
    tags=["Matches"],
)


@router.get("", response_model=list[MatchResultResponse])
async def get_matches(db: AsyncSession = Depends(get_db)):
    return await db.scalars(select(MatchResult))


@router.get("/official/{official_id}", response_model=list[MatchResultResponse])
async def get_matches_for_official(
    official_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await crud.get_matches_by_official(db, official_id)


@router.get("/{jurisdiction_slug}", response_model=list[MatchResultResponse])
async def get_matches_by_jurisdiction(
    jurisdiction_slug: str,
    db: AsyncSession = Depends(get_db),
):
    return await db.scalars(
        select(MatchResult)
        .join(Jurisdiction, MatchResult.jurisdiction_id == Jurisdiction.id)
        .where(Jurisdiction.slug == jurisdiction_slug)
    )
