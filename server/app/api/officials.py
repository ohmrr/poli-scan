from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from server.app.db.connection import get_db
from server.app.db.models import Official
from server.app.db import crud

router = APIRouter(
    prefix="/officials",
    tags=["Officials"],
)


@router.get("/search")
def search_officials(
    name: str,
    jurisdiction_slug: str | None = Query(
        default=None, description="Filter by jurisdiction slug, e.g. 'sonoma-county'"
    ),
    db: Session = Depends(get_db),
):
    query = db.query(Official).filter(
        Official.first_name.ilike(f"%{name}%") | Official.last_name.ilike(f"%{name}%")
    )

    if jurisdiction_slug:
        jurisdiction = crud.get_jurisdiction_by_slug(db, jurisdiction_slug)
        if not jurisdiction:
            raise HTTPException(
                status_code=404,
                detail=f"Jurisdiction '{jurisdiction_slug}' not found.",
            )
        query = query.filter(Official.jurisdiction_id == jurisdiction.id)

    results = query.order_by(Official.last_name, Official.first_name).all()

    return [
        {
            "id": r.id,
            "full_name": r.full_name,
            "jurisdiction_slug": r.jurisdiction.slug,
            "agency": r.agency,
            "holdings": [
                {"entity_name": h.entity_name, "year": h.year} for h in r.holdings
            ],
        }
        for r in results
    ]


@router.get("/{official_id}")
def get_official(official_id: int, db: Session = Depends(get_db)):
    official = crud.get_official_by_id(db, official_id)

    if not official:
        raise HTTPException(status_code=404, detail=f"Official with id '{official_id}' not found.")

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
