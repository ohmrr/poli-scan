from fastapi import APIRouter

# For getting jurisdictions from internal db
# WIP

router = APIRouter(
    prefix="/jurisdictions",
    tags=["Jurisdictions"],
)


@router.get("/")
def get_jurisdictions():
    return None
