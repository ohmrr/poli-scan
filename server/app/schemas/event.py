from pydantic import BaseModel, model_validator
from datetime import datetime
from typing import Any
from server.app.schemas.agenda_item import AgendaItemSummaryResponse


class EventSummaryResponse(BaseModel):
    id: int
    legistar_event_id: int | None
    body_name: str | None
    event_date: datetime | None
    agenda_item_count: int

    @model_validator(mode="before")
    @classmethod
    def compute_agenda_item_count(cls, data: Any) -> Any:
        if hasattr(data, "agenda_items"):
            data.__dict__["agenda_item_count"] = len(data.agenda_items)
        return data

    class Config:
        from_attributes = True


class EventDetailResponse(BaseModel):
    id: int
    legistar_event_id: int | None
    jurisdiction_slug: str
    body_name: str | None
    event_date: datetime | None
    agenda_items: list[AgendaItemSummaryResponse]

    @model_validator(mode="before")
    @classmethod
    def extract_jurisdiction_slug(cls, data: Any) -> Any:
        if hasattr(data, "jurisdiction") and data.jurisdiction:
            data.__dict__["jurisdiction_slug"] = data.jurisdiction.slug
        return data

    class Config:
        from_attributes = True
