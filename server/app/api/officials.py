from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from server.app.db.connection import get_db
from server.app.db.models import Official
from server.app.db import crud

router = APIRouter(
    prefix="/officials",
    tags=["Officials"],
)


@router.get("/{official_id}")
def get_official(official_id: int, db: Session = Depends(get_db)):
    official = db.query(Official).filter_by(id=official_id).first()

    if not official:
        return {"error": "Official not found"}

    return {
        "id": official.id,
        "full_name": official.full_name,
        "agency": official.agency,
        "position": official.position,
        "email": official.email,
        "legistar_person_id": official.legistar_person_id,
        "holdings": [
            {"entity_name": h.entity_name, "year": h.year} for h in official.holdings
        ],
    }
