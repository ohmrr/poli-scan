from sqlalchemy.orm import Session

from server.app.db import crud
from server.app.services.form700_parser import load_form700_csv
from server.app.services.legistar_client import LegistarClient


def ingest_form700(
    db: Session, jurisdiction_slug: str, csv_path: str, year: int
) -> dict:
    jurisdiction = crud.get_or_create_jurisdiction(db, slug=jurisdiction_slug)
    records = load_form700_csv(csv_path)

    officials_seen = 0
    holdings_seen = 0

    for record in records:
        official = crud.get_or_create_official(
            db,
            jurisdiction_id=jurisdiction.id,
            first_name=record.first_name,
            last_name=record.last_name,
            agency=record.agency,
            position=record.position,
        )

        officials_seen += 1

        for entity_name in record.holdings:
            crud.add_holding_if_missing(
                db, official_id=official.id, entity_name=entity_name, year=year
            )

            holdings_seen += 1

    return {
        "jurisdiction": jurisdiction_slug,
        "year": year,
        "officials_processed": officials_seen,
        "holdings_processed": holdings_seen,
    }


def ingest_legistar(db: Session, jurisdiction_slug: str, limit: int | None = None, start_date: str | None = None, end_date: str | None = None) -> dict:
    jurisdiction = crud.get_or_create_jurisdiction(db, slug=jurisdiction_slug)
    client = LegistarClient(jurisdiction_slug)

    try:
        persons = client.get_persons()
        for p in persons:
            existing = (
                db.query(crud.Official)
                .filter_by(
                    jurisdiction_id=jurisdiction.id,
                    first_name=p.first_name,
                    last_name=p.last_name,
                )
                .first()
            )
            if existing and not existing.legistar_person_id:
                existing.legistar_person_id = p.id
                existing.email = existing.email or p.email
        db.commit()
    except Exception as e:
        print(f"Warning: could not sync Legistar persons: {e}")

    scraped = client.scrape(limit=limit, start_date=start_date, end_date=end_date)

    events_seen = 0
    items_seen = 0

    for item in scraped:
        event = crud.get_or_create_event(
            db,
            jurisdiction_id=jurisdiction.id,
            legistar_event_id=item.event_id,
            event_date=item.event_date,
            body_name=item.body_name,
        )
        events_seen += 1

        crud.get_or_create_agenda_item(
            db,
            event_id=event.id,
            matter_id=item.matter_id,
            matter_type=item.matter_type,
            title=item.title,
            summary_report=item.summary_report,
        )
        items_seen += 1

    return {
        "jurisdiction": jurisdiction_slug,
        "events_processed": events_seen,
        "agenda_items_processed": items_seen,
    }
