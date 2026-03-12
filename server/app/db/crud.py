from sqlalchemy.orm import Session

from server.app.db.models import Jurisdiction, Official, Holding

# Jurisdictions


def get_jurisdiction_by_slug(db: Session, slug: str) -> Jurisdiction | None:
    return db.query(Jurisdiction).filter_by(slug=slug).first()


def get_or_create_jurisdiction(
    db: Session, slug: str, display_name: str | None = None
) -> Jurisdiction:
    record = get_jurisdiction_by_slug(db, slug)

    if record is None:
        record = Jurisdiction(slug=slug, display_name=display_name or slug)

        db.add(record)
        db.commit()
        db.refresh(record)

    return record


def list_jurisdictions(db: Session) -> list[Jurisdiction]:
    return db.query(Jurisdiction).order_by(Jurisdiction.slug).all()


# Officials


def get_official_by_id(db: Session, official_id: int):
    return db.query(Official).filter_by(id=official_id).first()


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
    record = (
        db.query(Official)
        .filter_by(
            jurisdiction_id=jurisdiction_id,
            last_name=last_name,
            first_name=first_name,
            agency=agency,
        )
        .first()
    )

    if record is None:
        record = Official(
            jurisdiction_id=jurisdiction_id,
            first_name=first_name,
            last_name=last_name,
            agency=agency,
            position=position,
            email=email,
            legistar_person_id=legistar_person_id,
        )

        db.add(record)
        db.commit()
        db.refresh(record)
    else:
        changed = False

        if email and not record.email:
            record.email = email
            changed = True

        if legistar_person_id and not record.legistar_person_id:
            record.legistar_person_id = legistar_person_id
            changed = True

        if changed:
            db.commit()
            db.refresh(record)

    return record


def list_officials(db: Session, jurisdiction_id: int) -> list[Official]:
    return (
        db.query(Official)
        .filter_by(jurisdiction_id=jurisdiction_id)
        .order_by(Official.last_name, Official.first_name)
        .all()
    )


# Holdings


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
