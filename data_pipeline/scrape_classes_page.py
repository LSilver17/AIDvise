"""
scrape_classes_page.py
-----------------------
Scrapes https://www.qcc.edu/classes for the full list of QCC credit courses.
For each course, also fetches the detail page to get description, credits,
prerequisites, and semesters_offered.

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
    """
    Fetch credits, description, prerequisites, and semesters_offered
    from a QCC course detail page.

    The page renders labeled fields as plain text in the <main> area, e.g.:
        Credits             3
        Semester Offered    F/S/SU
        [description paragraph]
        Prerequisites       Placement into college level English
    """
    result = {
        "description":      None,
        "prerequisites":    None,
        "credits":          None,
        "semesters_offered": None,
    }
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return result

        soup = BeautifulSoup(resp.text, "html.parser")
        main = soup.find("main") or soup.find("body")
        if not main:
            return result

        # Split into clean lines
        raw_lines = [clean_text(line) for line in main.get_text("\n").splitlines() if clean_text(line)]

        # --- Extract Credits ---
        for i, line in enumerate(raw_lines):
            if re.match(r"^Credits$", line, re.IGNORECASE):
                if i + 1 < len(raw_lines):
                    val = raw_lines[i + 1]
                    if re.match(r"^\d+(\.\d+)?$", val):
                        result["credits"] = val
                        break
            m = re.match(r"^Credits\s+(\d+(?:\.\d+)?)$", line, re.IGNORECASE)
            if m:
                result["credits"] = m.group(1)
                break

        # --- Extract Semesters Offered ---
        for i, line in enumerate(raw_lines):
            if re.match(r"^Semester[s]?\s+Offered$", line, re.IGNORECASE):
                if i + 1 < len(raw_lines):
                    result["semesters_offered"] = raw_lines[i + 1]
                    break
            m = re.match(r"^Semester[s]?\s+Offered\s{2,}(.+)$", line, re.IGNORECASE)
            if m:
                result["semesters_offered"] = clean_text(m.group(1))
                break
            m2 = re.match(r"^Semester[s]?\s+Offered[:\s]+(.+)$", line, re.IGNORECASE)
            if m2:
                val = clean_text(m2.group(1))
                if len(val) > 0:
                    result["semesters_offered"] = val
                    break

        # --- Extract Prerequisites ---
        for i, line in enumerate(raw_lines):
            if re.match(r"^Prerequisites?$", line, re.IGNORECASE):
                if i + 1 < len(raw_lines):
                    result["prerequisites"] = raw_lines[i + 1]
                    break
            m = re.match(r"^Prerequisites?\s{2,}(.+)$", line, re.IGNORECASE)
            if m:
                result["prerequisites"] = clean_text(m.group(1))
                break
            m2 = re.match(r"^Prerequisites?[:\s]+(.+)$", line, re.IGNORECASE)
            if m2:
                val = clean_text(m2.group(1))
                if len(val) > 2:
                    result["prerequisites"] = val
                    break

        # --- Extract Description ---
        label_pattern = re.compile(
            r"^(Area|Course Number|Semester[s]? Offered|Credits|Prerequisites?|"
            r"Skip to|Primary|Secondary|Contact|Visit|Apply|Copyright|"
            r"Local|Life-changing|Fulltext|Open Menu|Open Search)",
            re.IGNORECASE
        )
        content = main.find("article") or main
        text_blocks = []
        for el in content.find_all(["p", "div", "span"]):
            t = clean_text(el.get_text())
            if t:
                text_blocks.append(t)

        candidates = [t for t in text_blocks if len(t) > 80 and not label_pattern.match(t)]
        if candidates:
            result["description"] = max(candidates, key=len)

    except Exception:
        pass

    return result


def scrape_classes():
    print(f"Fetching {CLASSES_URL}...")
    resp = requests.get(CLASSES_URL, headers=HEADERS, timeout=30)
    soup = BeautifulSoup(resp.text, "html.parser")

    courses = []
    current_dept = None

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
                "course_code":      code,
                "department":       current_dept,
                "name":             name,
                "url":              full_url,
                "description":      None,
                "prerequisites":    None,
                "credits":          None,
                "semesters_offered": None,
                "scraped_at":       datetime.now().isoformat(),
            })

    print(f"Found {len(courses)} courses. Now fetching detail pages...\n")

    for i, course in enumerate(courses):
        print(f"[{i+1}/{len(courses)}] {course['course_code']} — {course['name']}")
        detail = fetch_course_detail(course["url"])
        course["description"]       = detail["description"]
        course["prerequisites"]     = detail["prerequisites"]
        course["credits"]           = detail["credits"]
        course["semesters_offered"] = detail["semesters_offered"]
        time.sleep(0.3)

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
    filled_credits  = sum(1 for c in courses if c["credits"] is not None)
    filled_semesters = sum(1 for c in courses if c["semesters_offered"] is not None)
    print(f"\n✅ Done in {elapsed}s")
    print(f"   Scraped {len(courses)} courses")
    print(f"   Credits populated:           {filled_credits}/{len(courses)}")
    print(f"   Semesters offered populated: {filled_semesters}/{len(courses)}")
    print(f"   Saved to {OUTPUT}")
    print("=" * 50)


if __name__ == "__main__":
    main()