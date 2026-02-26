import csv
from dataclasses import dataclass, field
from typing import List


@dataclass
class OfficialRecord:
    last_name: str
    first_name: str
    agency: str
    position: str
    holdings: List[str] = field(default_factory=list)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


def normalize_headers(headers: list[str]) -> list[str]:
    return [h.replace("\n", " ").strip() for h in headers]


def load_form700_csv(file_path: str) -> List[OfficialRecord]:
    officials: dict[str, OfficialRecord] = {}

    with open(file_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        reader.fieldnames = normalize_headers(reader.fieldnames or [])

        for row in reader:
            last = row.get("Last Name", "").strip()
            first = row.get("First Name", "").strip()
            agency = row.get("Agency", "").strip()
            position = row.get("Position", "").strip()
            holding = row.get("NAME OF BUSINESS ENTITY", "").strip()

            if not last and not first:
                continue

            key = f"{last},{first},{agency}"

            if key not in officials:
                officials[key] = OfficialRecord(
                    last_name=last, first_name=first, agency=agency, position=position
                )

            if holding:
                officials[key].holdings.append(holding)

    return list(officials.values())
