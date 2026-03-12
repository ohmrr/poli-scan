from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from server.app.db.connection import get_db
from server.app.db import crud
from server.app.db.models import Event

router = APIRouter(
    prefix="/events",
    tags=["Events"],
)


@router.get("/")
def list_events(
    jurisdiction_slug: str = Query(..., description="e.g. 'sacramento'"),
    body_name: str | None = Query(
        default=None, description="Filter by body name e.g. 'City Council'"
    ),
    db: Session = Depends(get_db),
):
    jurisdiction = crud.get_jurisdiction_by_slug(db, jurisdiction_slug)
    if not jurisdiction:
        raise HTTPException(
            status_code=404, detail=f"Jurisdiction '{jurisdiction_slug}' not found."
        )

    query = db.query(Event).filter_by(jurisdiction_id=jurisdiction.id)

    if body_name:
        query = query.filter(Event.body_name.ilike(f"%{body_name}%"))

    events = query.order_by(Event.event_date.desc()).all()

    return [
        {
            "id": e.id,
            "legistar_event_id": e.legistar_event_id,
            "body_name": e.body_name,
            "event_date": e.event_date,
            "agenda_item_count": len(e.agenda_items),
        }
        for e in events
    ]


@router.get("/{event_id}")
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter_by(id=event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")

    return {
        "id": event.id,
        "legistar_event_id": event.legistar_event_id,
        "jurisdiction_slug": event.jurisdiction.slug,
        "body_name": event.body_name,
        "event_date": event.event_date,
        "agenda_items": [
            {
                "id": item.id,
                "legistar_matter_id": item.legistar_matter_id,
                "matter_type": item.matter_type,
                "title": item.title,
                "has_summary": item.summary_report is not None,
            }
            for item in event.agenda_items
        ],
    }
