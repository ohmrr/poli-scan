from server.app.db.models import Official
"""
Bridge database data to the matching engine.
This file should:
1. load an official and their holdings from the database
2. find candidate agenda items from the database
3. map database fields into matcher input format
4. run the matcher on each candidate item
5. return flagged matches
"""

#testing matching engine service
async def run_matching_engine_for_offical(db,official_id: int, jurisdiction_slug: str): 
    official = db.query(Official).filter(Official.id == official_id).first()
    if not official:
        return {"Error": "Official not found/invalid official_id"}
    return {
        "official_id": official.id,
        "official_name": f"{official.first_name or ''} {official.last_name or ''}".strip(),
        "jurisdiction_slug": jurisdiction_slug,
        "holdings_count": len(official.holdings),
        "matches_found": 0,
        "matches": [],
    }