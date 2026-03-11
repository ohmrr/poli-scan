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


class ScrapedMeetings(BaseModel):
    Jurisdiction: Optional[str] = None
    EventId: Optional[int] = None
    EventDate: Optional[str] = None
    BodyName: Optional[str] = None
    MatterId: Optional[int] = None
    MatterType: Optional[str] = None
    Title: Optional[str] = None
    Attachments: Optional[list[dict]] = None
    SummaryReport: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "ScrapedMeetings":
        return cls(
            Jurisdiction=data.get("Jurisdiction"),
            EventId=data.get("EventId"),
            EventDate=data.get("EventDate"),
            BodyName=data.get("BodyName"),
            MatterId=data.get("MatterId"),
            MatterType=data.get("MatterType"),
            Title=data.get("Title"),
            Attachments=data.get("Attachments"),
            SummaryReport=data.get("SummaryReport"),
        )
