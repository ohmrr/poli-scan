from pydantic import BaseModel
from datetime import datetime


class MatchResultResponse(BaseModel):
    id: int
    official_id: int
    jurisdiction_id: int
    agenda_item_id: int | None
    matched_interest: str
    confidence: float
    flagged: bool
    reason: str | None
    pdf_url: str | None
    attachment_name: str | None
    event_date: str | None
    year: int
    created_at: datetime

    class Config:
        from_attributes = True
