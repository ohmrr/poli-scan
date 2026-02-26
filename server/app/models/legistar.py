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


class Agenda(BaseModel):
    id: int
    title: Optional[str] = None
    fileDate: Optional[str] = None
    status: Optional[str] = None

    @classmethod
    def from_legistar(cls, data: dict) -> "Agenda":
        return cls(
            id=data.get("MatterId"),
            title=data.get("MatterTitle"),
            fileDate=data.get("MatterFile"),
            status=data.get("MatterStatusName"),
        )
