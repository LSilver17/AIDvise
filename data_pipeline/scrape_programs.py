"""
scrape_programs.py
-------------------
Scrapes https://www.qcc.edu/programs for all QCC programs of study.
For each program, fetches the detail page to get required courses.

Outputs: qcc_programs.json

SETUP:
    pip install requests beautifulsoup4

USAGE:
    python scrape_programs.py
"""

import json
import re
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime

BASE_URL    = "https://www.qcc.edu"
PROGRAMS_URL = "https://www.qcc.edu/programs"
OUTPUT      = "qcc_programs.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def clean_text(text):
    return " ".join(text.split()).strip()


def fetch_program_detail(url):
    """Fetch required courses and description from a program detail page."""
    result = {
        "description":     None,
        "total_credits":   None,
        "required_courses": [],
    }
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return result
        soup = BeautifulSoup(resp.text, "html.parser")

        # Get description
        for selector in [".field--name-body", ".field--type-text-with-summary", "main .field p"]:
            el = soup.select_one(selector)
            if el:
                text = clean_text(el.get_text())
                if len(text) > 30:
                    result["description"] = text
                    break

        # Get total credits
        full_text = soup.get_text()
        credit_match = re.search(r"Total(?:\s+Program)?\s+Credits?:?\s*(\d+)", full_text, re.IGNORECASE)
        if credit_match:
            result["total_credits"] = int(credit_match.group(1))

        # Get required courses — look for course codes in tables or lists
        courses = []
        for el in soup.find_all(["td", "li", "p"]):
            text = clean_text(el.get_text())
            matches = re.findall(r"\b([A-Z]{2,4}\s+\d{3}[A-Z]?)\b", text)
            for m in matches:
                if m not in courses:
                    courses.append(m)

        result["required_courses"] = courses

    except Exception as e:
        pass
    return result


def scrape_programs():
    print(f"Fetching {PROGRAMS_URL}...")
    resp = requests.get(PROGRAMS_URL, headers=HEADERS, timeout=30)
    soup = BeautifulSoup(resp.text, "html.parser")

    programs = []
    current_area = None

    main = soup.find("main") or soup.find("body")

    for el in main.find_all(["h2", "tr"]):
        if el.name == "h2":
            current_area = clean_text(el.get_text())

        elif el.name == "tr":
            cells = el.find_all("td")
            if len(cells) < 2:
                continue

            link = cells[0].find("a")
            if not link:
                continue

            name = clean_text(link.get_text())
            href = link.get("href", "")
            degree_type = clean_text(cells[1].get_text()) if len(cells) > 1 else None
            full_url = BASE_URL + href if href.startswith("/") else href

            if not name:
                continue

            programs.append({
                "name":             name,
                "area_of_study":    current_area,
                "degree_type":      degree_type,
                "url":              full_url,
                "description":      None,
                "total_credits":    None,
                "required_courses": [],
                "scraped_at":       datetime.now().isoformat(),
            })

    print(f"Found {len(programs)} programs. Fetching detail pages...\n")

    for i, program in enumerate(programs):
        print(f"[{i+1}/{len(programs)}] {program['name']}")
        detail = fetch_program_detail(program["url"])
        program["description"]      = detail["description"]
        program["total_credits"]    = detail["total_credits"]
        program["required_courses"] = detail["required_courses"]
        time.sleep(0.3)

    return programs


def main():
    start = datetime.now()
    print("=" * 50)
    print("  QCC Programs of Study Scraper")
    print(f"  {start.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    programs = scrape_programs()

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(programs, f, indent=2)

    elapsed = (datetime.now() - start).seconds
    print(f"\n✅ Done in {elapsed}s")
    print(f"   Scraped {len(programs)} programs")
    print(f"   Saved to {OUTPUT}")
    print("=" * 50)


if __name__ == "__main__":
    main()