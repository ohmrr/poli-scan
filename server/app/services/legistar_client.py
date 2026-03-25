import requests
import pdfplumber
import io
from server.app.models.legistar import AgendaItem, Person

LEGISTAR_BASE_URL = "https://webapi.legistar.com/v1"

FETCH_MATTER_TYPES = {
    "Consent Calendar Item",
    "Regular Calendar Item",
}

SUMMARY_TYPES = {
    "summary report",
    "summary",
}

ADMIN_ACCOUNT_NAMES = {
    "Granicus",
    "View",
    "Legistar",
    "System",
    "Administrator",
}


class LegistarClient:
    def __init__(self, client: str):
        """
        client example:
        - 'sacramento'
        - 'sonoma-county'
        """
        self.client = client
        self.base = f"{LEGISTAR_BASE_URL}/{client}"

    def _fetch(self, endpoint: str, params: dict = None) -> list | dict:
        url = f"{self.base}/{endpoint}"

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        return response.json()

    def get_persons(self) -> list[Person]:
        try:
            raw = self._fetch("Persons")
        except requests.RequestException as e:
            print(f"Couldn't fetch persons for '{self.client}': {e}")
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

    def get_final_events(self, 
                         limit: int | None = None, 
                         start_date: str | None = None, 
                         end_date: str | None = None,
                         ) -> list[dict]:
        params = {"$orderby": "EventId desc"}
        if limit is not None:
            params["$top"] = limit
        if start_date and end_date:
            params["$filter"] = f"EventDate ge datetime'{start_date}' and EventDate le datetime'{end_date}'"
        elif start_date:
            params["$filter"] = f"EventDate ge datetime'{start_date}'"
        elif end_date:
            params["$filter"] = f"EventDate le datetime'{end_date}'"
        try:
            data = self._fetch("Events", params=params)
        except requests.RequestException as e:
            print(f"Couldn't fetch events for '{self.client}': {e}")
            return []

        return [m for m in data if m.get("EventAgendaStatusName") == "Final"]

    def get_event_items(self, event_id: int) -> list[dict]:
        try:
            return self._fetch(f"Events/{event_id}/EventItems")
        except requests.RequestException as e:
            print(f"Couldn't fetch event items for '{self.client}': {e}")
            return []

    def get_attachments(self, matter_id: int) -> list[dict]:
        try:
            raw = self._fetch(f"Matters/{matter_id}/Attachments")
        except requests.RequestException as e:
            print(f"Couldn't fetch attachments for '{self.client}': {e}")
            return []

        return [
            {"name": a["MatterAttachmentName"], "link": a["MatterAttachmentHyperlink"]}
            for a in raw
            if a.get("MatterAttachmentName") and a.get("MatterAttachmentHyperlink")
        ]

    def find_summary_report(self, attachments: list[dict]) -> dict | None:
        for a in attachments:
            lower_name = a.get("name", "").lower()

            if any(k in lower_name for k in SUMMARY_TYPES):
                return a

        return None

    def pdf_extract(self, url: str) -> str | None:
        try:
            response = requests.get(url, timeout=20)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Couldn't download attachment: {e}")
            return None

        try:
            pages = []
            with pdfplumber.open(io.BytesIO(response.content)) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        pages.append(text)
            return "\n".join(pages) if pages else None
        except Exception as e:
            print(f"Couldn't extract pdf: {e}")
            return None

    def scrape(self, limit: int | None = None, start_date: str | None = None, end_date: str | None = None) -> list[AgendaItem]:
        events = self.get_final_events(limit, 
                                       start_date, 
                                       end_date)

        if not events:
            print(f"No events found for '{self.client}'")
            return []

        results = []

        for e in events:
            event_id = e["EventId"]
            event_date = e.get("EventDate", "")
            event_body = e.get("EventBodyName", "")

            print(
                f"\nEventId: {event_id} | EventDate: {event_date} | EventBody: {event_body}"
            )

            items = self.get_event_items(event_id)
            agendas = [a for a in items if a.get("EventItemMatterId") is not None]

            print(f"{len(agendas)} agenda items found")

            for i in agendas:
                matter_id = i.get("EventItemMatterId")
                title = i.get("EventItemTitle", "")
                matter_type = i.get("EventItemMatterType", "")

                report = {
                    "jurisdiction": self.client,
                    "event_id": event_id,
                    "event_date": event_date,
                    "body_name": event_body,
                    "matter_id": matter_id,
                    "matter_type": matter_type,
                    "title": title,
                    "attachments": [],
                    "summary_report": None,
                }

                if matter_type not in FETCH_MATTER_TYPES:
                    results.append(AgendaItem.from_dict(report))
                    continue

                attachments = self.get_attachments(matter_id)
                report["attachments"] = attachments

                if not attachments:
                    results.append(AgendaItem.from_dict(report))
                    continue

                summary = self.find_summary_report(attachments)
                if not summary:
                    results.append(AgendaItem.from_dict(report))
                    continue

                pdf_text = self.pdf_extract(summary["link"])
                if pdf_text:
                    report["summary_report"] = pdf_text
                else:
                    print("Couldn't extract text from Summary Report")

                results.append(AgendaItem.from_dict(report))

        return results
