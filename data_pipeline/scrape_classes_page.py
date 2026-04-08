"""
scrape_classes_page.py
-----------------------
Scrapes https://www.qcc.edu/classes for the full list of QCC credit courses.
For each course, also fetches the detail page to get the description.

Outputs: qcc_classes.json

SETUP:
    pip install requests beautifulsoup4

USAGE:
    python scrape_classes_page.py
"""

import json
import re
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime

BASE_URL    = "https://www.qcc.edu"
CLASSES_URL = "https://www.qcc.edu/classes"
OUTPUT      = "qcc_classes.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def clean_text(text):
    return " ".join(text.split()).strip()


def fetch_course_detail(url):
    """Fetch description and prerequisites from a course detail page."""
    result = {"description": None, "prerequisites": None, "credits": None}
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return result
        soup = BeautifulSoup(resp.text, "html.parser")

        # Description is usually in the main content area
        # Try common selectors
        desc = None
        for selector in [
            ".field--name-body",
            ".field--type-text-with-summary",
            "article .field",
            "main p"
        ]:
            el = soup.select_one(selector)
            if el:
                text = clean_text(el.get_text())
                if len(text) > 50:
                    desc = text
                    break

        if desc:
            # Extract prerequisites
            prereq_match = re.search(r"Prerequisite[s]?:\s*(.+?)(?:\.|$)", desc, re.IGNORECASE)
            if prereq_match:
                result["prerequisites"] = clean_text(prereq_match.group(1))

            # Extract credits
            credit_match = re.search(r"(\d+(?:\.\d+)?)\s+credit", desc, re.IGNORECASE)
            if credit_match:
                result["credits"] = credit_match.group(1)

            result["description"] = desc

    except Exception as e:
        pass
    return result


def scrape_classes():
    print(f"Fetching {CLASSES_URL}...")
    resp = requests.get(CLASSES_URL, headers=HEADERS, timeout=30)
    soup = BeautifulSoup(resp.text, "html.parser")

    courses = []
    current_dept = None

    # Find all department headings and course table rows
    main = soup.find("main") or soup.find("body")

    for el in main.find_all(["h2", "tr"]):
        if el.name == "h2":
            current_dept = clean_text(el.get_text())

        elif el.name == "tr":
            cells = el.find_all("td")
            if len(cells) < 2:
                continue

            code = clean_text(cells[0].get_text())
            if not re.match(r"[A-Z]{2,4}\s+\d+", code):
                continue

            link = cells[1].find("a")
            if not link:
                continue

            name = clean_text(link.get_text())
            href = link.get("href", "")
            full_url = BASE_URL + href if href.startswith("/") else href

            courses.append({
                "course_code":  code,
                "department":   current_dept,
                "name":         name,
                "url":          full_url,
                "description":  None,
                "prerequisites": None,
                "credits":      None,
                "scraped_at":   datetime.now().isoformat(),
            })

    print(f"Found {len(courses)} courses. Now fetching detail pages...\n")

    for i, course in enumerate(courses):
        print(f"[{i+1}/{len(courses)}] {course['course_code']} — {course['name']}")
        detail = fetch_course_detail(course["url"])
        course["description"]  = detail["description"]
        course["prerequisites"] = detail["prerequisites"]
        course["credits"]       = detail["credits"]
        time.sleep(0.3)  # be polite to the server

    return courses


def main():
    start = datetime.now()
    print("=" * 50)
    print("  QCC Classes Page Scraper")
    print(f"  {start.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    courses = scrape_classes()

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(courses, f, indent=2)

    elapsed = (datetime.now() - start).seconds
    print(f"\n✅ Done in {elapsed}s")
    print(f"   Scraped {len(courses)} courses")
    print(f"   Saved to {OUTPUT}")
    print("=" * 50)


if __name__ == "__main__":
    main()