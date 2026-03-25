from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from server.app.services.form700_parser import load_form700_csv
from server.app.services.legistar_client import LegistarClient

from server.app.services.ingestion import ingest_form700, ingest_legistar

from server.app.api import jurisdictions, officials, events, agenda_items

from server.app.db.connection import get_db
from server.app.db.init_db import init_db

app = FastAPI(
    title="FPPC Conflict of Interest Identifier",
    version="0.0.1",
)


@app.on_event("startup")
def startup():
    init_db()


app.include_router(jurisdictions.router)
app.include_router(officials.router)
app.include_router(events.router)
app.include_router(agenda_items.router)

print("API Documentation - http://127.0.0.1:8000/docs")


@app.get("/")
def root():
    return {"message": "FPPC API is running successfully!"}


@app.post("/ingest/form700/{client_name}/{year}")
def ingest_form700_endpoint(
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
    return ingest_form700(
        db, jurisdiction_slug=client_name, csv_path=csv_path, year=year
    )


@app.post("/ingest/legistar/{client_name}")
def ingest_legistar_endpoint(
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
    return ingest_legistar(
        db,
        jurisdiction_slug=client_name, 
        limit=limit, 
        start_date=start_date, 
        end_date=end_date)
