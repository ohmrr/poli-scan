from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from server.app.db.connection import get_db
from server.app.db import crud
from server.app.db.models import Jurisdiction

router = APIRouter(
    prefix="/jurisdictions",
    tags=["Jurisdictions"],
)


@router.get("/")
def get_jurisdictions(db: Session = Depends(get_db)):
    records = crud.list_jurisdictions(db)
    return [
        {
            "id": r.id,
            "slug": r.slug,
            "display_name": r.display_name,
            "officials": r.officials,
        }
        for r in records
    ]


@router.get("/{slug}")
def get_jurisdiction(slug: str, db: Session = Depends(get_db)):
    jurisdiction = crud.get_jurisdiction_by_slug(db, slug)

    if not jurisdiction:
        raise HTTPException(
            status_code=404, detail=f"Jurisdiction '{slug}' was not found."
        )

    return {
        "id": jurisdiction.id,
        "slug": jurisdiction.slug,
        "display_name": jurisdiction.display_name,
        "uses_legistar": jurisdiction.uses_legistar,
    }


@router.get("/{slug}/officials")
def get_jurisdiction_officials(slug: str, db: Session = Depends(get_db)):
    jurisdiction = crud.get_jurisdiction_by_slug(db, slug)

    if not jurisdiction:
        raise HTTPException(
            status_code=404, detail=f"Jurisdiction '{slug}' was not found."
        )

    records = crud.list_officials(db, jurisdiction_id=jurisdiction.id)
    return [
        {
            "id": r.id,
            "legistar_person_id": r.legistar_person_id,
            "jurisdiction_id": jurisdiction.id,
            "jurisdiction_slug": jurisdiction.slug,
            "first_name": r.first_name,
            "last_name": r.last_name,
            "full_name": r.full_name,
            "email": r.email,
            "agency": r.agency,
            "position": r.position,
        }
        for r in records
    ]


@router.get("/{slug}/officials/{official_id}/holdings")
def get_official_holdings(slug: str, official_id: int, db: Session = Depends(get_db)):
    jurisdiction = crud.get_jurisdiction_by_slug(db, slug)
    if not jurisdiction:
        raise HTTPException(
            status_code=404,
            detail=f"Jurisdiction '{slug}' not found.",
        )
    
    official = crud.get_official_by_id(db, official_id)
    if not official or official.jurisdiction_id != jurisdiction.id:
        raise HTTPException(
            status_code=404,
            detail=f"Official '{official_id}' not found in jurisdiction '{slug}'.",
        )

    return [
        {
            "id": h.id,
            "entity_name": h.entity_name,
            "year": h.year,
        }
        for h in official.holdings
    ]
