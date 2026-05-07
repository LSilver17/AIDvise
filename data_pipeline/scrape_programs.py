"""
scrape_programs.py
-------------------
Scrapes https://www.qcc.edu/programs for all QCC programs of study.
For each program, fetches the detail page to get description, total credits,
area of study, and required courses.

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

BASE_URL     = "https://www.qcc.edu"
PROGRAMS_URL = "https://www.qcc.edu/programs"
OUTPUT       = "qcc_programs.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def clean_text(text):
    return " ".join(text.split()).strip()


def area_from_url(url):
    """
    Extract area of study from URL path.
    e.g. https://www.qcc.edu/applied-technologies/some-program
         -> "Applied Technologies"
    """
    match = re.search(r"qcc\.edu/([^/]+)/", url)
    if match:
        slug = match.group(1)
        return slug.replace("-", " ").title()
    return None


def fetch_program_detail(url):
    """
    Fetch description, total_credits, and required_courses
    from a QCC program detail page.

    Description  = paragraph(s) directly under the <h1> title
    total_credits = "Total Credits Required" cell in the curriculum table
    required_courses = course codes from the curriculum table
    """
    result = {
        "description":      None,
        "total_credits":    None,
        "required_courses": [],
    }
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return result

        soup = BeautifulSoup(resp.text, "html.parser")
        main = soup.find("main") or soup.find("body")
        if not main:
            return result

        # --- Description ---
        # Find the first substantial paragraph that reads like a real program description.
        # QCC pages nest content in divs so we can't rely on h1 siblings alone.
        skip_pattern = re.compile(
            r"^(Certificate|Associate|This semester|Become an|Apply|Submit|Meet with|"
            r"Skip to|Contact|Visit|Open Menu|Fulltext|Local|Life-changing|Copyright|"
            r"In-State|Out-of-State|Some programs|This program may be|High School|"
            r"Ways to Take|Requirements|Locations|Timeline|Cost|Program Overview|"
            r"What Will You Learn|Curriculum|Connections|Career|Have more questions)",
            re.IGNORECASE
        )
        for el in main.find_all(["p", "div"]):
            text = clean_text(el.get_text())
            if len(text) > 80 and not skip_pattern.match(text):
                if re.search(
                    r"(program|students|learn|career|degree|skills|course|prepares?|provides?|designed|pathway)",
                    text, re.IGNORECASE
                ):
                    result["description"] = text
                    break

        # --- Total Credits & Required Courses from curriculum table ---
        courses = []
        for table in main.find_all("table"):
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all(["td", "th"])
                if not cells:
                    continue

                row_text = clean_text(row.get_text())

                # Total credits row
                if re.search(r"Total\s+Credits?\s+Required", row_text, re.IGNORECASE):
                    # Last cell with a number is the credit count
                    for cell in reversed(cells):
                        num = re.search(r"\b(\d+)\b", clean_text(cell.get_text()))
                        if num:
                            result["total_credits"] = int(num.group(1))
                            break

                # Course code cells — e.g. "ELT 103"
                for cell in cells:
                    text = clean_text(cell.get_text())
                    matches = re.findall(r"\b([A-Z]{2,4}\s+\d{3}[A-Z]?)\b", text)
                    for m in matches:
                        if m not in courses:
                            courses.append(m)

        result["required_courses"] = courses

    except Exception:
        pass

    return result


def scrape_programs():
    print(f"Fetching {PROGRAMS_URL}...")
    resp = requests.get(PROGRAMS_URL, headers=HEADERS, timeout=30)
    soup = BeautifulSoup(resp.text, "html.parser")

    programs = []

    main = soup.find("main") or soup.find("body")

    for el in main.find_all(["h2", "tr"]):
        if el.name == "tr":
            cells = el.find_all("td")
            if len(cells) < 1:
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
                "area_of_study":    area_from_url(full_url),
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
    filled_desc    = sum(1 for p in programs if p["description"] is not None)
    filled_credits = sum(1 for p in programs if p["total_credits"] is not None)
    filled_area    = sum(1 for p in programs if p["area_of_study"] is not None)
    print(f"\n✅ Done in {elapsed}s")
    print(f"   Scraped {len(programs)} programs")
    print(f"   Descriptions populated:  {filled_desc}/{len(programs)}")
    print(f"   Total credits populated: {filled_credits}/{len(programs)}")
    print(f"   Area of study populated: {filled_area}/{len(programs)}")
    print(f"   Saved to {OUTPUT}")
    print("=" * 50)


if __name__ == "__main__":
    main()