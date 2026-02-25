from fastapi import APIRouter

# For getting officials from internal db
# WIP

router = APIRouter(prefix="/officials", tags=["/Officials"])


@router.get("/")
def get_officials():
    return None


@router.get("/{official_id}")
def get_official():
    return None
