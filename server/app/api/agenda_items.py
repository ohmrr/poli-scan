from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from server.app.db.connection import get_db
from server.app.db.models import AgendaItem

router = APIRouter(
    prefix="/agenda-items",
    tags=["Agenda Items"],
)


@router.get("/search")
def search_agenda_items(
    q: str = Query(..., description="Search term matched against title and summary"),
    jurisdiction_slug: str | None = Query(
        default=None, description="Narrow to a specific jurisdiction"
    ),
    db: Session = Depends(get_db),
):
    """
    Full text search across agenda item titles and summary reports.
    This is the core endpoint for finding agenda items that might relate
    to an official's stock holdings.
    """
    from server.app.db import crud
    from server.app.db.models import Event, Jurisdiction

    query = (
        db.query(AgendaItem)
        .join(Event)
        .join(Jurisdiction)
        .filter(
            AgendaItem.title.ilike(f"%{q}%") | AgendaItem.summary_report.ilike(f"%{q}%")
        )
    )

    if jurisdiction_slug:
        jurisdiction = crud.get_jurisdiction_by_slug(db, jurisdiction_slug)
        if not jurisdiction:
            raise HTTPException(
                status_code=404, detail=f"Jurisdiction '{jurisdiction_slug}' not found."
            )
        query = query.filter(Event.jurisdiction_id == jurisdiction.id)

    results = query.order_by(AgendaItem.id.desc()).limit(50).all()

    return [
        {
            "id": item.id,
            "legistar_matter_id": item.legistar_matter_id,
            "matter_type": item.matter_type,
            "title": item.title,
            "has_summary": item.summary_report is not None,
            "event": {
                "id": item.event.id,
                "body_name": item.event.body_name,
                "event_date": item.event.event_date,
                "jurisdiction_slug": item.event.jurisdiction.slug,
            },
        }
        for item in results
    ]


@router.get("/{item_id}")
def get_agenda_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(AgendaItem).filter_by(id=item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Agenda item not found.")

    return {
        "id": item.id,
        "legistar_matter_id": item.legistar_matter_id,
        "matter_type": item.matter_type,
        "title": item.title,
        "summary_report": item.summary_report,
        "event": {
            "id": item.event.id,
            "legistar_event_id": item.event.legistar_event_id,
            "body_name": item.event.body_name,
            "event_date": item.event.event_date,
            "jurisdiction_slug": item.event.jurisdiction.slug,
        },
    }
