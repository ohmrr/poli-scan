import requests
import json
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from urllib.parse import urljoin
from datetime import datetime


SANTA_ANA_MEETING_LIST_URL = "https://santa-ana.primegov.com/api/meeting/list"
SANTA_ANA_BASE_URL = "https://santa-ana.primegov.com"


def extract_items_with_attachments(soup):
    items = []
    current_section = None

    for tag in soup.find_all("div"):
        text = tag.get_text(" ", strip=True)
        text_upper = text.upper()

        if "CONSENT CALENDAR" in text_upper:
            current_section = "Consent Calendar"
            continue

        if "BUSINESS CALENDAR" in text_upper:
            current_section = "Business Calendar"
            continue

        classes = tag.get("class", [])

        if "meeting-item" not in classes:
            continue

        if tag.get("data-hasattachments", "").lower() != "true":
            continue

        agenda_div = tag.find("div", class_="agenda-item")
        if not agenda_div:
            continue

        full_text = agenda_div.get_text(" ", strip=True)
        title = full_text.split("Department:")[0].strip()

        attachments = []

        for a in tag.find_all("a", href=True):
            href = a["href"]
            name = a.get_text(" ", strip=True)

            if href and href != "#":
                full_link = urljoin(SANTA_ANA_BASE_URL, href)
                attachments.append({
                    "name": name,
                    "link": full_link,
                })

        items.append({
            "title": title,
            "matter_type": current_section,
            "attachments": attachments,
        })

    return items


def get_santa_ana_meetings() -> list[dict]:
    response = requests.get(
        SANTA_ANA_MEETING_LIST_URL,
        timeout=20,
        verify=False,
    )

    response.raise_for_status()
    return response.json()


def find_agenda_template(meeting: dict) -> dict | None:
    for template in meeting.get("templates", []):
        if template.get("title") == "Agenda":
            return template

    return None


def build_meeting_url(template_id) -> str:
    return f"{SANTA_ANA_BASE_URL}/Portal/Meeting?meetingTemplateId={template_id}"


def fetch_page_html(url: str) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto(url, wait_until="networkidle", timeout=60000)
            page.wait_for_selector("div.meeting-item", timeout=30000)

            agenda_items = page.locator("div.agenda-item")
            count = agenda_items.count()

            for i in range(count):
                try:
                    agenda_items.nth(i).click(timeout=3000)
                    page.wait_for_timeout(800)
                except Exception:
                    pass

            return page.content()

        except PlaywrightTimeoutError:
            return page.content()

        finally:
            browser.close()


def scrape_santa_ana(limit: int = 5) -> list[dict]:
    meetings = get_santa_ana_meetings()

    meetings = sorted(
        meetings,
        key=lambda meeting: datetime.fromisoformat(
            meeting["dateTime"].replace("Z", "+00:00")
        ),
        reverse=True,
    )

    results = []

    for meeting in meetings[:limit]:
        agenda_template = find_agenda_template(meeting)

        if not agenda_template:
            continue

        meeting_url = build_meeting_url(agenda_template.get("id"))
        print("URL:", meeting_url)

        html = fetch_page_html(meeting_url)
        html_lower = html.lower()

        if (
            "document not found" in html_lower
            or "requested meeting document is no longer available" in html_lower
        ):
            continue

        soup = BeautifulSoup(html, "html.parser")
        items = extract_items_with_attachments(soup)

        for item in items:
            results.append({
                "jurisdiction": "santa-ana",
                "event_date": meeting.get("dateTime"),
                "body_name": meeting.get("title"),
                "title": item["title"],
                "matter_type": item["matter_type"],
                "attachments": item["attachments"],
            })

    return results


if __name__ == "__main__":
    items = scrape_santa_ana(limit=3)

    print(json.dumps(items, indent=2))