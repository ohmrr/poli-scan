STOPWORDS = {"the", "of", "and", "a", "an", "inc", 
             "llc", "corp", "co", "trust", "family"}
def get_keywords(holdings: list[dict], year: int) -> list[str]:
    results = []
    for holding in holdings:
        if holding["year"] == year:
            words = holding["entity_name"].lower().split()
            for word in words:
                if word not in STOPWORDS and len(word) > 2:
                    results.append(word)
    return results
def prefilter(keywords: list[str], agenda_item: dict) -> bool:
    title = agenda_item.get("EventItemTitle", "").lower()
    summary = agenda_item.get("EventItemSummary", "").lower()

    for k in keywords:
        if k in title :
            return True
        if k in summary:
            return True
    return False