from typing import Optional

from pydantic import BaseModel


class Person(BaseModel):
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None

    @classmethod
    def from_legistar(cls, data: dict) -> "Person":
        return cls(
            id=data.get("PersonId"),
            first_name=data.get("PersonFirstName"),
            last_name=data.get("PersonLastName"),
            email=data.get("PersonEmail"),
        )


class AgendaItem(BaseModel):
    jurisdiction: Optional[str] = None
    event_id: Optional[int] = None
    event_item_id: Optional[int] = None
    event_date: Optional[str] = None
    body_name: Optional[str] = None
    matter_id: Optional[int] = None
    matter_type: Optional[str] = None
    title: Optional[str] = None
    attachments: Optional[list[dict]] = None

    @classmethod
    def from_dict(cls, data: dict) -> "AgendaItem":
        return cls(
            jurisdiction=data.get("jurisdiction"),
            event_id=data.get("event_id"),
            event_item_id=data.get("event_item_id"),
            event_date=data.get("event_date"),
            body_name=data.get("body_name"),
            matter_id=data.get("matter_id"),
            matter_type=data.get("matter_type"),
            title=data.get("title"),
            attachments=data.get("attachments"),
        )
