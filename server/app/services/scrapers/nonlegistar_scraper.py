import requests
import json
from bs4 import BeautifulSoup
import re

SANTA_ANA_MEETING_LIST_URL = "https://santa-ana.primegov.com/api/meeting/list"

def print_has_attachments_context(html):
    match = re.search(r"data-hasattachments", html)
    if match:
        start = max(0, match.start() - 500)
        end = min(len(html), match.start() + 1500)
        print("\nHTML AROUND data-hasattachments:\n")
        print(html[start:end])
    else:
        print("No data-hasattachments found in HTML")

def extract_items_with_attachments(soup):
    items = []

    for tag in soup.find_all("div", class_="meeting-item"):
        if tag.get("data-hasattachments") == "True":

            # find the title area
            agenda_div = tag.find("div", class_="agenda-item")
            if not agenda_div:
                continue

            full_text = agenda_div.get_text(" ", strip=True)
            title = full_text.split("Department:")[0].strip()       

            # get attachment links
            attachments = []
            for a in tag.find_all("a", href=True):
                href = a["href"]
                name = a.get_text(" ", strip=True)

                if "/meeting/attachment/" in href:
                    full_link = "https://santa-ana.primegov.com" + href
                    attachments.append({
                        "name": name,
                        "link": full_link
                    })

            items.append({
                "title": title,
                "attachments": attachments
            })

    return items

def get_santa_ana_meetings() -> list[dict]:
    # Call the Santa Ana API to get meeting data
    response = requests.get(
        SANTA_ANA_MEETING_LIST_URL,
        timeout=20,
        verify=False  # ignore SSL certificate issues 
    )

    
    response.raise_for_status()

    return response.json()


def find_agenda_template(meeting: dict) -> dict | None:
    # list of templates from each meeting
    for template in meeting.get("templates", []):
        # Look for the one labeled "Agenda"
        if template.get("title") == "Agenda":
            return template

    return None


def build_meeting_url(template_id) -> str:
    # Build the URL for the meeting page using the template ID
    return f"https://santa-ana.primegov.com/Portal/Meeting?meetingTemplateId={template_id}"

def fetch_page_html(url: str) -> str:
    response = requests.get(url, timeout=20, verify=False)
    response.raise_for_status()
    return response.text

def scrape_santa_ana(limit: int = 1) -> list[dict]:

    meetings = get_santa_ana_meetings()

    results = []
 
    for meeting in meetings[:limit]:
        print("\nMEETING:", meeting.get("title"))

        #find the Agenda template inside this meeting
        agenda_template = find_agenda_template(meeting)

        if not agenda_template:
            print("No Agenda template found.")
            continue 

        #build the meeting page URL
        meeting_url = build_meeting_url(agenda_template.get("id"))

        html = fetch_page_html(meeting_url)
        soup = BeautifulSoup(html, "html.parser")

        items = extract_items_with_attachments(soup)

        print("ITEM COUNT:", len(items))
        for item in items[:2]:
            print(" -", item["title"])

        #create one AgendaItem (placeholder for now)
        for item in items:
            results.append({
                "jurisdiction": "santa-ana",
                "event_date": meeting.get("dateTime"),
                "body_name": meeting.get("title"),
                "title": item["title"],
                "matter_type": None,
                "attachments": item["attachments"],
    })
    return results

if __name__ == "__main__":
    items = scrape_santa_ana(limit=5)

    print("\nFINAL OUTPUT:\n")
    for item in items:
        print(json.dumps(item, indent=2))