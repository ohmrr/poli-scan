import requests
import pdfplumber
import io
from server.app.models.legistar import ScrapedMeetings, Person

LEGISTAR_BASE_URL = "https://webapi.legistar.com/v1"

FETCH_MATTER_TYPES = {
    "Consent Calendar Item",
    "Regular Calendar Item",
}
SUMMARY_TYPES = {
    "summary report",
    "summary",
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

    def _fetch(self, endpoint: str, params: dict = None):
        url = f"{self.base}/{endpoint}"
        return url

    def get_persons(self) -> list[Person]:
        # GET https://webapi.legistar.com/v1/{client}/Persons
        rdata = requests.get(self._fetch("Persons"), params=None, timeout=10)
        raw = rdata.json()

        admin_account_names = [
            "Granicus",
            "View",
            "Legistar",
            "System",
            "Administrator",
        ]

        people = []
        for person in raw:
            # Ignore inactive persons.
            # Might need to change this if we need to look at agendas were
            # previous employees participated in
            if person.get("PersonActiveFlag") != 1:
                continue

            first_name = person.get("PersonFirstName") or ""
            last_name = person.get("PersonlastName") or ""
            email = person.get("PersonEmail") or ""

            # Remove Legistar & Granicus Admin/Test accounts
            if first_name in admin_account_names or last_name in admin_account_names:
                continue

            if email.endswith("granicus.com"):
                continue

            # Transform data to match Person model, getting rid of unnecessary data
            people.append(Person.from_legistar(person))

        return people

    def get_final_events(self, limit: int) -> list[dict]:
        params = {"$top": limit, "$orderby": "EventId desc", "$skip": 0}
        r = self._fetch("Events")

        try:
            response = requests.get(r, params=params, timeout=10)
            response.raise_for_status()
            d = response.json()
        except requests.RequestException as e:
            print(f"Couldn't fetch events for '{self.client}': {e}")
            return []

        final = []

        for m in d:
            if m.get("EventAgendaStatusName") == "Final":
                final.append(m)

        return final

    def get_event_items(self, event_id: int) -> list[dict]:
        url = f"{self._fetch('Events')}/{event_id}/EventItems"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Couldn't fetch events items for '{self.client}': {e}")
            return []

    def get_attachments(self, matter_id: int) -> list[dict]:
        url = f"{self._fetch( 'Matters')}/{matter_id}/Attachments"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            rdata = response.json()
        except requests.RequestException as e:
            print(f"Couldn't fetch attachments for '{self.client}': {e}")
            return []

        attachments = []

        for a in rdata:
            name = a.get("MatterAttachmentName", "")
            link = a.get("MatterAttachmentHyperlink", "")

            if name and link:
                attachments.append({"name": name, "link": link})

        return attachments

    def find_summary_report(self, attachments: list[dict]) -> dict | None:
        for a in attachments:
            lowerName = a.get("name", "").lower()
            for k in SUMMARY_TYPES:
                if k in lowerName:
                    return a
        return None

    def pdf_extract(self, url: str) -> str | None:
        try:
            response = requests.get(url, timeout=20)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Couldn't download attachments:{e}")
            return None

        try:
            rdata = io.BytesIO(response.content)

            with pdfplumber.open(rdata) as pdf:
                pages = []

                for page in pdf.pages:
                    text = page.extract_text()

                    if text:
                        pages.append(text)

                if pages:
                    return "\n".join(pages)
                else:
                    return None
        except Exception as e:
            print(f"Couldn't extract pdf:{e}")

            return None

    def scrape(self, limit: int) -> list[dict]:
        events = self.get_final_events(limit)

        if not events:
            print(f"No events found for '{self.client}'")
            return []

        results = []

        for e in events:
            eventId = e["EventId"]
            eventDate = e.get("EventDate", "")
            eventBody = e.get("EventBodyName", "")

            print(
                f"\nEventId: {eventId} | EventDate: {eventDate} | EventBody: {eventBody}"
            )

            items = self.get_event_items(eventId)
            agendas = []

            for a in items:
                if a.get("EventItemMatterId") is not None:
                    agendas.append(a)

            print(f"{len(agendas)} agendas items found")

            for i in agendas:
                matter_id = i.get("EventItemMatterId")
                title = i.get("EventItemTitle", "")
                matter_type = i.get("EventItemMatterType", "")

                report = {
                    "Jurisdiction": self.client,
                    "EventId": eventId,
                    "EventDate": eventDate,
                    "BodyName": eventBody,
                    "MatterId": matter_id,
                    "MatterType": matter_type,
                    "Title": title,
                    "Attachments": [],
                    "SummaryReport": None,
                }

                if matter_type not in FETCH_MATTER_TYPES:
                    results.append(ScrapedMeetings.from_dict(report))
                    continue

                attachments = self.get_attachments(matter_id)
                report["Attachments"] = attachments

                if not attachments:
                    results.append(ScrapedMeetings.from_dict(report))
                    continue

                summary = self.find_summary_report(attachments)
                if not summary:
                    results.append(ScrapedMeetings.from_dict(report))
                    continue

                pdfText = self.pdf_extract(summary["link"])
                if pdfText:
                    report["SummaryReport"] = pdfText
                else:
                    print("Couldn't extract text from Summary Report")

                results.append(ScrapedMeetings.from_dict(report))

        return results
