from pydantic import BaseModel


class JurisdictionResponse(BaseModel):
    id: int
    slug: str
    display_name: str | None
    uses_legistar: bool

    class Config:
        from_attributes = True
