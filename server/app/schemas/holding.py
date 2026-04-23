from pydantic import BaseModel

class HoldingResponse(BaseModel):
    entity_name: str
    year: int | None

    class Config:
        from_attributes = True
