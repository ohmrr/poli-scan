import asyncio
import logging

import httpx

from server.app.models.legistar import AgendaItem, Person

logger = logging.getLogger(__name__)

LEGISTAR_BASE_URL = "https://webapi.legistar.com/v1"

FETCH_MATTER_TYPES = {
    "Consent Calendar Item",
    "Regular Calendar Item",
}

ADMIN_ACCOUNT_NAMES = {
    "Granicus",
    "View",
    "Legistar",
    "System",
    "Administrator",
}


class LegistarClient:
    def __init__(self, jurisdiction: str):
        self.jurisdiction = jurisdiction
        self.base = f"{LEGISTAR_BASE_URL}/{jurisdiction}"
        self._client = httpx.AsyncClient(timeout=10.0)
        self._sem = asyncio.Semaphore(10)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self._client.aclose()

    async def _fetch(self, endpoint: str, params: dict = None) -> list | dict:
        url = f"{self.base}/{endpoint}"
        async with self._sem:
            response = await self._client.get(url, params=params)
            response.raise_for_status()

            return response.json()

    async def get_persons(self) -> list[Person]:
        try:
            raw = await self._fetch("Persons")
        except httpx.RequestError as e:
            logger.warning("Couldn't fetch persons for '%s': %s", self.jurisdiction, e)
            return []

        people = []
        for person in raw:
            if person.get("PersonActiveFlag") != 1:
                continue

            first_name = person.get("PersonFirstName") or ""
            last_name = person.get("PersonLastName") or ""
            email = person.get("PersonEmail") or ""

            if first_name in ADMIN_ACCOUNT_NAMES or last_name in ADMIN_ACCOUNT_NAMES:
                continue

            if email.endswith("granicus.com"):
                continue

            people.append(Person.from_legistar(person))

        return people

    async def get_final_events(
        self,
        limit: int | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[dict]:
        params = {"$orderby": "EventId desc"}

        if limit is not None:
            params["$top"] = limit

        if start_date and end_date:
            params["$filter"] = (
                f"EventDate ge datetime'{start_date}' and EventDate le datetime'{end_date}'"
            )
        elif start_date:
            params["$filter"] = f"EventDate ge datetime'{start_date}'"
        elif end_date:
            params["$filter"] = f"EventDate le datetime'{end_date}'"

        try:
            data = await self._fetch("Events", params=params)
        except httpx.RequestError as e:
            logger.warning("Couldn't fetch events for '%s': %s", self.jurisdiction, e)
            return []

        return [m for m in data if m.get("EventAgendaStatusName") == "Final"]

    async def get_event_items(self, event_id: int) -> list[dict]:
        try:
            return await self._fetch(f"Events/{event_id}/EventItems")
        except httpx.RequestError as e:
            logger.warning(
                "Couldn't fetch event items for '%s': %s", self.jurisdiction, e
            )
            return []

    async def get_attachments(self, matter_id: int) -> list[dict]:
        try:
            raw = await self._fetch(f"Matters/{matter_id}/Attachments")
        except httpx.RequestError as e:
            logger.warning(
                "Couldn't fetch attachments for '%s': %s", self.jurisdiction, e
            )
            return []

        return [
            {"name": a["MatterAttachmentName"], "link": a["MatterAttachmentHyperlink"]}
            for a in raw
            if a.get("MatterAttachmentName") and a.get("MatterAttachmentHyperlink")
        ]

    async def scrape(
        self,
        limit: int | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[AgendaItem]:
        events = await self.get_final_events(limit, start_date, end_date)

        if not events:
            logger.warning("No events found for '%s'", self.jurisdiction)
            return []

        # Fetch all event items in parallel
        event_items_list = await asyncio.gather(
            *[self.get_event_items(e["EventId"]) for e in events]
        )

        results = []

        for e, items in zip(events, event_items_list):
            event_id = e["EventId"]
            event_date = e.get("EventDate", "")
            event_body = e.get("EventBodyName", "")

            agendas = [a for a in items if a.get("EventItemMatterId") is not None]

            logger.info(
                "EventId: %s | EventDate: %s | EventBody: %s",
                event_id,
                event_date,
                event_body,
            )
            logger.info("%s agenda items found", len(agendas))
            
            matters_needing_attachments = [
                a for a in agendas if a.get("EventItemMatterType") in FETCH_MATTER_TYPES
            ]

            # Fetch all attachments in parallel
            attachment_results = await asyncio.gather(
                *[
                    self.get_attachments(a["EventItemMatterId"])
                    for a in matters_needing_attachments
                ]
            )
            attachment_map = {
                a["EventItemMatterId"]: atts
                for a, atts in zip(matters_needing_attachments, attachment_results)
            }

            for i in agendas:
                matter_id = i.get("EventItemMatterId")
                report = {
                    "jurisdiction": self.jurisdiction,
                    "event_id": event_id,
                    "event_date": event_date,
                    "body_name": event_body,
                    "matter_id": matter_id,
                    "matter_type": i.get("EventItemMatterType", ""),
                    "title": i.get("EventItemTitle", ""),
                    "attachments": attachment_map.get(matter_id, []),
                }
                results.append(AgendaItem.from_dict(report))

        return results
