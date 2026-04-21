import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from server.app.config import settings
from server.app.logger import setup_logging

setup_logging()


from server.app.api import agenda_items, events, jurisdictions, officials, matches
from server.app.db.connection import get_db, init_db
from server.app.services.ingestion import ingest_form700, ingest_legistar
from server.app.services.matching_engine import llm_providers, matching_utils
from server.app.services.matching_engine.service import run_matching_engine_for_official

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()

    logger.info("Database initialized")
    logger.info("Running in %s mode", settings.ENV)

    yield

    await llm_providers.close()
    await matching_utils.close()


app = FastAPI(
    title="FPPC Conflict of Interest Identifier", version="0.0.1", lifespan=lifespan
)

app.include_router(jurisdictions.router)
app.include_router(officials.router)
app.include_router(events.router)
app.include_router(agenda_items.router)
app.include_router(matches.router)

logger.info("API Documentation - http://127.0.0.1:8000/docs")


@app.get("/")
def root():
    return {"message": "FPPC API is running successfully!"}


@app.post("/ingest/form700/{client_name}/{year}")
async def ingest_form700_endpoint(
    client_name: str,
    year: int,
    db: Session = Depends(get_db),
):
    """
    Parse the Form 700 CSV for a jurisdiction+year and store
    officials + holdings in the database.

    Expects a file at:  ./server/app/data/{client_name}-{year}.csv
    """
    csv_path = f"./server/app/data/{client_name}-{year}.csv"
    return await ingest_form700(
        db, jurisdiction_slug=client_name, csv_path=csv_path, year=year
    )


@app.post("/ingest/legistar/{client_name}")
async def ingest_legistar_endpoint(
    client_name: str,
    limit: int | None = 1,
    start_date: str | None = None,
    end_date: str | None = None,
    db: Session = Depends(get_db),
):
    """
    Scrape up to `limit` final events from Legistar and store
    events + agenda items in the database.
    Date filters:
    - start_date: YYYY-MM-DD
    - end_date: YYYY-MM-DD
    """
    return await ingest_legistar(
        db,
        jurisdiction_slug=client_name,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
    )


@app.post("/matching/official/{official_id}")
async def run_matching_engine_for_official_endpoint(
    official_id: int,
    jurisdiction_slug: str,
    db: Session = Depends(get_db),
):
    """
    Run the matching engine for a given official and return flagged matches.
    """

    return await run_matching_engine_for_official(db, official_id, jurisdiction_slug)
