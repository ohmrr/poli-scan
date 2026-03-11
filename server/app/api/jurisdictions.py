from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from server.app.db.connection import get_db
from server.app.db import crud

router = APIRouter(
    prefix="/jurisdictions",
    tags=["Jurisdictions"],
)


@router.get("/")
def get_jurisdictions(db: Session = Depends(get_db)):
    records = crud.list_jurisdictions(db)
    return [
        {
            "id": record.id,
            "slug": record.slug,
            "display_name": record.display_name,
            "officials": record.officials,
        }
        for record in records
    ]


@router.get("/{jurisdiction_id}")
def get_jurisdiction(jurisdiction_id: str, db: Session = Depends(get_db)):
    return None
