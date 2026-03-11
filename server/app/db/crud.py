from sqlalchemy.orm import Session

from server.app.db.models import Jurisdiction, Official, Holding


def get_or_create_jurisdiction(
    db: Session, slug: str, display_name: str | None = None
) -> Jurisdiction:
    jurisdiction_record = db.query(Jurisdiction).filter_by(slug=slug).first()

    if jurisdiction_record is None:
        jurisdiction_record = Jurisdiction(slug=slug, display_name=display_name or slug)

        db.add(jurisdiction_record)
        db.commit()
        db.refresh(jurisdiction_record)

    return jurisdiction_record


def list_jurisdictions(db: Session) -> list[Jurisdiction]:
    return db.query(Jurisdiction).order_by(Jurisdiction.slug).all()


def get_or_create_official(
    db: Session,
    jurisdiction_id: int,
    first_name: str | None,
    last_name: str | None,
    agency: str | None,
    *,
    position: str | None = None,
    email: str | None = None,
    legistar_person_id: int | None = None,
) -> Official:
    official_record = (
        db.query(Official)
        .filter_by(
            jurisdiction_id=jurisdiction_id,
            last_name=last_name,
            first_name=first_name,
            agency=agency,
        )
        .first()
    )

    if official_record is None:
        official_record = Official(
            jurisdiction_id=jurisdiction_id,
            first_name=first_name,
            last_name=last_name,
            agency=agency,
            position=position,
            email=email,
            legistar_person_id=legistar_person_id,
        )

        db.add(official_record)
        db.commit()
        db.refresh(official_record)
    else:
        changed = False

        if email and not official_record.email:
            official_record.email = email
            changed = True

        if legistar_person_id and not official_record.legistar_person_id:
            official_record.legistar_person_id = legistar_person_id
            changed = True

        if changed:
            db.commit()
            db.refresh(official_record)

    return official_record


def list_officials(db: Session, jurisdiction_id: int) -> list[Official]:
    return (
        db.query(Official)
        .filter_by(jurisdiction_id=jurisdiction_id)
        .order_by(Official.last_name, Official.first_name)
        .all()
    )


def add_holding_if_missing(
    db: Session, official_id: int, entity_name: str, year: int | None
) -> Holding:
    holding_record = (
        db.query(Holding)
        .filter_by(official_id=official_id, entity_name=entity_name, year=year)
        .first()
    )

    if holding_record is None:
        holding_record = Holding(
            official_id=official_id, entity_name=entity_name, year=year
        )

        db.add(holding_record)
        db.commit()
        db.refresh(holding_record)

    return holding_record
