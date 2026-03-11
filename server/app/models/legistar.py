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
    event_date: Optional[str] = None
    body_name: Optional[str] = None
    matter_id: Optional[int] = None
    matter_type: Optional[str] = None
    title: Optional[str] = None
    attachments: Optional[list[dict]] = None
    summary_report: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "AgendaItem":
        return cls(
            jurisdiction=data.get("Jurisdiction"),
            event_id=data.get("EventId"),
            event_date=data.get("EventDate"),
            body_name=data.get("BodyName"),
            matter_id=data.get("MatterId"),
            matter_type=data.get("MatterType"),
            title=data.get("Title"),
            attachments=data.get("Attachments"),
            summary_report=data.get("SummaryReport"),
        )
