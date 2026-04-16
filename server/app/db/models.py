from datetime import datetime
from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Jurisdiction(Base):
    __tablename__ = "jurisdictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(100))
    uses_legistar: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    officials: Mapped[list["Official"]] = relationship(
        back_populates="jurisdiction", cascade="all, delete-orphan"
    )

    events: Mapped[list["Event"]] = relationship(
        back_populates="jurisdiction", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Jurisdiction slug={self.slug!r}>"


class Official(Base):
    __tablename__ = "officials"
    __table_args__ = (
        UniqueConstraint("jurisdiction_id", "last_name", "first_name", "agency"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    jurisdiction_id: Mapped[int] = mapped_column(
        ForeignKey("jurisdictions.id", ondelete="CASCADE"), nullable=False
    )
    legistar_person_id: Mapped[int | None] = mapped_column(Integer)
    first_name: Mapped[str | None] = mapped_column(String(50))
    last_name: Mapped[str | None] = mapped_column(String(50))
    email: Mapped[str | None] = mapped_column(String(100))
    agency: Mapped[str | None] = mapped_column(String(100))
    position: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    jurisdiction: Mapped["Jurisdiction"] = relationship(back_populates="officials")
    holdings: Mapped[list["Holding"]] = relationship(
        back_populates="official", cascade="all, delete-orphan"
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name or ''} {self.last_name or ''}".strip()

    def __repr__(self) -> str:
        return f"<Official {self.full_name!r} agency={self.agency!r}>"


class Holding(Base):
    __tablename__ = "holdings"
    __table_args__ = (UniqueConstraint("official_id", "entity_name", "year"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    official_id: Mapped[int] = mapped_column(
        ForeignKey("officials.id", ondelete="CASCADE"),
        nullable=False,
    )
    entity_name: Mapped[str] = mapped_column(String(100), nullable=False)
    year: Mapped[int | None] = mapped_column(Integer)

    official: Mapped["Official"] = relationship(back_populates="holdings")

    def __repr__(self) -> str:
        return f"<Holding {self.entity_name!r} year={self.year}>"


class Event(Base):
    __tablename__ = "events"
    __table_args__ = (UniqueConstraint("jurisdiction_id", "legistar_event_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    jurisdiction_id: Mapped[int] = mapped_column(
        ForeignKey("jurisdictions.id", ondelete="CASCADE"), nullable=False
    )
    legistar_event_id: Mapped[int | None] = mapped_column(Integer)
    body_name: Mapped[str | None] = mapped_column(String(100))
    event_date: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    jurisdiction: Mapped["Jurisdiction"] = relationship(back_populates="events")
    agenda_items: Mapped[list["AgendaItem"]] = relationship(
        back_populates="event", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Event legistar_event_id={self.legistar_event_id!r} date={self.event_date!r}>"


class AgendaItem(Base):
    __tablename__ = "agenda_items"
    __table_args__ = (UniqueConstraint("event_id", "legistar_matter_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id", ondelete="CASCADE"), nullable=False
    )
    legistar_matter_id: Mapped[int | None] = mapped_column(Integer)
    matter_type: Mapped[str | None] = mapped_column(String(100))
    title: Mapped[str | None] = mapped_column(Text)
    attachment_items: Mapped[list["AttachmentItem"]] = relationship(
        back_populates="agenda_item", cascade="all, delete-orphan"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    event: Mapped["Event"] = relationship(back_populates="agenda_items")

    def __repr__(self) -> str:
        return f"<AgendaItem matter_id={self.legistar_matter_id!r} type={self.matter_type!r}>"


class AttachmentItem(Base):
    __tablename__ = "attachment_items"
    __table_args__ = (UniqueConstraint("agenda_item_id", "url"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agenda_item_id: Mapped[int] = mapped_column(
        ForeignKey("agenda_items.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str | None] = mapped_column(Text)
    url: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    agenda_item: Mapped["AgendaItem"] = relationship(back_populates="attachment_items")

    def __repr__(self) -> str:
        return f"<AttachmentItem name={self.name!r} url={self.url!r}>"
