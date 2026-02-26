from turtle import title

import requests

from server.app.models.legistar import Agenda, Person

LEGISTAR_BASE_URL = "https://webapi.legistar.com/v1"


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

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        return response.json()

    def get_persons(self) -> list[Person]:
        # GET https://webapi.legistar.com/v1/{client}/Persons
        raw = self._fetch("Persons")

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

    def get_agendas(self, limit: int) -> list[Agenda]:
        # GET https://webapi.legistar.com/v1/{client}/Matters
        # params:
        #   $top = how many results to return
        #   $orderby = sort by MatterId (highest first, so newest-ish first)
        raw = self._fetch(
            "Matters", params={"$top": limit, "$orderby": "MatterId desc"}
        )

        agendas = []  # this will store the cleaned Agenda objects we return
        for matter in raw:
            # Only keep items that are ready to be put on an agenda
            # If it is not "Agenda Ready", skip it
            if matter.get("MatterStatusName") != "Agenda Ready":
                continue
            # Convert the raw Legistar dictionary into our Agenda model
            # (This usually picks out fields like MatterId, MatterFile, MatterTitle, dates, etc.)
            agendas.append(Agenda.from_legistar(matter))
        # Return the list of Agenda objects
        return agendas
