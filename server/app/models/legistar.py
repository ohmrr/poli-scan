from pydantic import BaseModel
from typing import Optional


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
