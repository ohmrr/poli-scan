from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from server.app.db import crud
from server.app.db.connection import get_db
from server.app.schemas.jurisdiction import JurisdictionResponse
from server.app.schemas.official import OfficialResponse
from server.app.schemas.holding import HoldingResponse

router = APIRouter(
    prefix="/jurisdictions",
    tags=["Jurisdictions"],
)


async def get_jurisdiction_or_404(slug: str, db: AsyncSession):
    jurisdiction = await crud.get_jurisdiction_by_slug(db, slug)
    if not jurisdiction:
        raise HTTPException(
            status_code=404, detail=f"Jurisdiction '{slug}' was not found."
        )
    return jurisdiction


@router.get("", response_model=list[JurisdictionResponse])
async def get_jurisdictions(db: AsyncSession = Depends(get_db)):
    return await crud.list_jurisdictions(db)


@router.get("/{slug}", response_model=JurisdictionResponse)
async def get_jurisdiction(slug: str, db: AsyncSession = Depends(get_db)):
    return await get_jurisdiction_or_404(slug, db)


@router.get("/{slug}/officials", response_model=list[OfficialResponse])
async def get_jurisdiction_officials(slug: str, db: AsyncSession = Depends(get_db)):
    jurisdiction = await get_jurisdiction_or_404(slug, db)
    return await crud.list_officials(db, jurisdiction_id=jurisdiction.id)


@router.get(
    "/{slug}/officials/{official_id}/holdings", response_model=list[HoldingResponse]
)
async def get_official_holdings(
    slug: str, official_id: int, db: AsyncSession = Depends(get_db)
):
    jurisdiction = await get_jurisdiction_or_404(slug, db)
    official = await crud.get_official_by_id(db, official_id)
    if not official or official.jurisdiction_id != jurisdiction.id:
        raise HTTPException(
            status_code=404,
            detail=f"Official '{official_id}' not found in jurisdiction '{slug}'.",
        )
    return official.holdings
