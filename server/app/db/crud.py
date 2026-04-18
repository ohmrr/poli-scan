from sqlalchemy import join, select
from sqlalchemy.ext.asyncio import AsyncSession

from server.app.db.models import (
    AgendaItem,
    AttachmentItem,
    Event,
    Holding,
    Jurisdiction,
    Official,
)

# Jurisdictions


async def get_jurisdiction_by_slug(db: AsyncSession, slug: str) -> Jurisdiction | None:
    result = await db.execute(select(Jurisdiction).where(Jurisdiction.slug == slug))
    return result.scalars().first()


async def get_or_create_jurisdiction(
    db: AsyncSession, slug: str, display_name: str | None = None
) -> Jurisdiction:
    record = await get_jurisdiction_by_slug(db, slug)

    if record is None:
        record = Jurisdiction(slug=slug, display_name=display_name or slug)

        db.add(record)
        await db.commit()
        await db.refresh(record)

    return record


async def list_jurisdictions(db: AsyncSession) -> list[Jurisdiction]:
    result = await db.execute(select(Jurisdiction).order_by(Jurisdiction.slug))
    return result.scalars().all()


# Officials


async def get_official_by_id(db: AsyncSession, official_id: int):
    result = await db.execute(select(Official).where(Official.id == official_id))
    return result.scalars().first()


async def get_or_create_official(
    db: AsyncSession,
    jurisdiction_id: int,
    first_name: str | None,
    last_name: str | None,
    agency: str | None,
    *,
    position: str | None = None,
    email: str | None = None,
    legistar_person_id: int | None = None,
) -> Official:
    result = await db.execute(
        select(Official).filter_by(
            jurisdiction_id=jurisdiction_id,
            last_name=last_name,
            first_name=first_name,
            agency=agency,
        )
    )

    record = result.scalars().first()

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
        await db.commit()
        await db.refresh(record)
    else:
        changed = False

        if email and not record.email:
            record.email = email
            changed = True

        if legistar_person_id and not record.legistar_person_id:
            record.legistar_person_id = legistar_person_id
            changed = True

        if changed:
            await db.commit()
            await db.refresh(record)

    return record


async def list_officials(db: AsyncSession, jurisdiction_id: int) -> list[Official]:
    result = await db.execute(
        select(Official)
        .where(Official.jurisdiction_id == jurisdiction_id)
        .order_by(Official.last_name, Official.first_name)
    )
    return result.scalars().all()


# Holdings


async def add_holding_if_missing(
    db: AsyncSession, official_id: int, entity_name: str, year: int | None
) -> Holding:
    result = await db.execute(
        select(Holding).where(
            Holding.official_id == official_id,
            Holding.entity_name == entity_name,
            Holding.year == year,
        )
    )

    holding_record = result.scalars().first()

    if holding_record is None:
        holding_record = Holding(
            official_id=official_id, entity_name=entity_name, year=year
        )

        db.add(holding_record)
        await db.commit()
        await db.refresh(holding_record)

    return holding_record


# Events


async def get_or_create_event(
    db: AsyncSession,
    jurisdiction_id: int,
    legistar_event_id: int | None,
    event_date: str | None,
    body_name: str | None,
) -> Event:
    result = await db.execute(
        select(Event).where(
            Event.jurisdiction_id == jurisdiction_id,
            Event.legistar_event_id == legistar_event_id,
        )
    )

    record = result.scalars().first()

    if record is None:
        record = Event(
            jurisdiction_id=jurisdiction_id,
            legistar_event_id=legistar_event_id,
            event_date=event_date,
            body_name=body_name,
        )

        db.add(record)
        await db.commit()
        await db.refresh(record)

    return record


# Agenda


async def get_or_create_agenda_item(
    db: AsyncSession,
    event_id: int,
    matter_id: int | None,
    matter_type: str | None,
    title: str | None,
) -> AgendaItem:
    result = await db.execute(
        select(AgendaItem).filter_by(event_id=event_id, legistar_matter_id=matter_id)
    )

    record = result.scalars().first()

    if record is None:
        record = AgendaItem(
            event_id=event_id,
            legistar_matter_id=matter_id,
            matter_type=matter_type,
            title=title,
        )

        db.add(record)
        await db.commit()
        await db.refresh(record)


async def get_agenda_items_by_jurisdiction_and_year(
    db: AsyncSession, jurisdiction_id: int, year: int
) -> list[AgendaItem]:
    result = await db.execute(
        select(AgendaItem)
        .join(Event)
        .where(
            Event.jurisdiction_id == jurisdiction_id, Event.event_date.like(f"{year}%")
        )
    )

    return result.scalars().all()


# Attachments


async def get_or_create_attachment_items(
    db: AsyncSession, agenda_item_id: int, name: str, url: str | None
) -> AttachmentItem:
    result = await db.execute(
        select(AttachmentItem).filter_by(agenda_item_id=agenda_item_id, url=url)
    )

    record = result.scalars().first()

    if record is None:
        record = AttachmentItem(agenda_item_id=agenda_item_id, name=name, url=url)

        db.add(record)
        await db.commit()
        await db.refresh(record)

    return record
