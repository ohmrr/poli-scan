import io
import re

import httpx
import pdfplumber


def fetch_pdf_text(url: str) -> str:
    response = httpx.get(url, verify=False, timeout=30)
    response.raise_for_status()
    with pdfplumber.open(io.BytesIO(response.content)) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)


def _clean_names(raw: str) -> list[str]:
    if not raw or re.match(r"^\s*none\s*", raw, re.IGNORECASE):
        return []
    raw = re.sub(r"\(\d+\)\s*$", "", raw).strip()
    names = re.split(r",\s*", raw)
    cleaned = []
    for name in names:
        name = re.sub(r"(?i)councilmember\s+", "", name).strip()
        name = re.sub(r"(?i)mayor\s+pro\s+tem\s+", "", name).strip()
        name = re.sub(r"(?i)mayor\s+", "", name).strip()
        if name:
            cleaned.append(name)
    return cleaned


def parse_votes(text: str) -> list[dict]:
    votes = []

    # Old format: VOTE: AYES: ... (N) NOES: ... (0) ABSTAIN: ... (0) ABSENT: ... (0)
    old = re.compile(
        r"VOTE:\s*AYES:\s*(.*?)\s*\(\d+\)\s*"
        r"NOES:\s*(.*?)\s*\(\d+\)\s*"
        r"ABSTAIN:\s*(.*?)\s*\(\d+\)\s*"
        r"ABSENT:\s*(.*?)\s*\(\d+\)",
        re.DOTALL | re.IGNORECASE,
    )
    for m in old.finditer(text):
        votes.append({
            "ayes": _clean_names(m.group(1)),
            "noes": _clean_names(m.group(2)),
            "abstain": _clean_names(m.group(3)),
            "absent": _clean_names(m.group(4)),
        })

    # New format: The motion carried/failed, N-N, by the following roll call vote:
    new = re.compile(
        r"motion (?:carried|failed)[^\n]*\n"
        r"AYES:\s*(.*?)\s*NOES:\s*(.*?)\s*ABSTAIN:\s*(.*?)(?:\s*ABSENT:\s*(.*?))?(?=\n\n|\Z)",
        re.DOTALL | re.IGNORECASE,
    )
    for m in new.finditer(text):
        votes.append({
            "ayes": _clean_names(m.group(1)),
            "noes": _clean_names(m.group(2)),
            "abstain": _clean_names(m.group(3)),
            "absent": _clean_names(m.group(4)) if m.group(4) else [],
        })

    return votes
