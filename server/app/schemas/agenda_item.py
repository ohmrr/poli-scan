from pydantic import BaseModel, model_validator
from typing import Any


class AgendaItemSummaryResponse(BaseModel):
    id: int
    legistar_matter_id: int | None
    matter_type: str | None
    title: str | None

    class Config:
        from_attributes = True


class AgendaItemDetailResponse(BaseModel):
    id: int
    legistar_matter_id: int | None
    matter_type: str | None
    title: str | None
    event_id: int | None
    event_date: str | None
    body_name: str | None
    jurisdiction_slug: str | None

    @model_validator(mode="before")
    @classmethod
    def extract_event_fields(cls, data: Any) -> Any:
        if hasattr(data, "event") and data.event:
            data.__dict__["event_date"] = data.event.event_date
            data.__dict__["body_name"] = data.event.body_name
            if data.event.jurisdiction:
                data.__dict__["jurisdiction_slug"] = data.event.jurisdiction.slug
        return data

    class Config:
        from_attributes = True
