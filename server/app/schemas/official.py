from server.app.schemas.holding import HoldingResponse
from pydantic import BaseModel, model_validator
from typing import Any


class OfficialResponse(BaseModel):
    id: int
    full_name: str
    jurisdiction_id: int
    jurisdiction_slug: str
    agency: str | None
    position: str | None
    email: str | None
    legistar_person_id: int | None
    holdings: list[HoldingResponse]

    @model_validator(mode="before")
    @classmethod
    def extract_jurisdiction_slug(cls, data: Any) -> Any:
        if hasattr(data, "jurisdiction") and data.jurisdiction:
            data.__dict__["jurisdiction_slug"] = data.jurisdiction.slug
        return data

    class Config:
        from_attributes = True
