# =============================================================================
# CSC 212 — AI Academic Advising Platform
# Data Pipeline

# Copyright (c) 2026 Quinsigamond Community College — CSC 212
# All rights reserved.

# Author:   Noel Mensah
# GitHub:   https://github.com/LSilver17/CSC212---AI-Agent

# =============================================================================

"""
@file scrape_programs.py
@brief Scrapes the public QCC website for all programs of study with full details.

@details
This module scrapes https://www.qcc.edu/programs for the complete list of QCC
academic programs and certificates, then visits each program's detail page to extract:
    - Program description
    - Total credits required
    - Area of study (derived from the URL path)
    - List of required course codes

Like scrape_classes_page.py, this scraper uses Requests and BeautifulSoup
since the public QCC website renders content statically. Area of study is
derived from the URL path rather than page headings, which proved unreliable.
Description extraction scans all content elements for the first substantial
paragraph containing program-related keywords, since QCC wraps descriptions
in nested div elements rather than placing them as direct siblings of headings.

@date 2026

@par Input
    https://www.qcc.edu/programs — public QCC programs listing page

@par Output
    qcc_programs.json — list of program dictionaries with full detail fields

@par Dependencies
    - requests
    - beautifulsoup4
    - json (stdlib)
    - re (stdlib)
    - time (stdlib)

@par Usage
    python scrape_programs.py
"""

import json
import re
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime

## @brief Base URL for constructing absolute links from relative hrefs.
BASE_URL     = "https://www.qcc.edu"

## @brief URL of the QCC public programs listing page.
PROGRAMS_URL = "https://www.qcc.edu/programs"

## @brief Output path for the scraped JSON file.
OUTPUT       = "qcc_programs.json"

## @brief HTTP headers to send with each request to mimic a browser.
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def clean_text(text):
    """
    @brief Removes excess whitespace from a string.

    @param text The raw string to clean.
    @return A normalized single-line string with no extra whitespace.
    """
    return " ".join(text.split()).strip()


def area_from_url(url):
    """
    @brief Derives the area of study from the program's URL path segment.

    @details
    QCC program URLs follow the pattern:
        https://www.qcc.edu/[area-slug]/[program-slug]

    This function extracts the area slug from the first path segment after
    the domain and converts it to title case (e.g. "applied-technologies"
    becomes "Applied Technologies").

    This approach is more reliable than parsing <h2> tags from the programs
    listing page, which did not consistently match program entries.

    @param url The full URL of the program detail page.
    @return The area of study as a title-cased string, or None if the URL
            does not contain a recognizable path segment.

    @par Example
    @code
    area_from_url("https://www.qcc.edu/applied-technologies/some-program")
    # -> "Applied Technologies"
    @endcode
    """
    match = re.search(r"qcc\.edu/([^/]+)/", url)
    if match:
        slug = match.group(1)
        return slug.replace("-", " ").title()
    return None


def fetch_program_detail(url):
    """
    @brief Fetches and extracts detail fields from a QCC program detail page.

    @details
    Sends an HTTP GET request to the program detail URL and parses the response.
    Extracts three categories of information:

    Description:
        Scans all <p> and <div> elements in the main content area for the first
        block exceeding 80 characters that contains program-related keywords
        (program, students, learn, career, degree, skills, course, prepares,
        provides, designed, pathway). Blocks matching navigation or boilerplate
        patterns are skipped. This approach handles QCC's nested div structure
        where the description is not a direct sibling of the <h1> heading.

    Total Credits:
        Searches all curriculum tables for a row containing "Total Credits Required"
        and reads the numeric value from the last cell of that row.

    Required Courses:
        Collects all course codes matching the pattern "[A-Z]{2,4} [0-9]{3}" from
        all curriculum table cells, preserving order and deduplicating.

    @param url The full URL of the program detail page.
    @return A dictionary with keys:
            - "description" (str or None)
            - "total_credits" (int or None)
            - "required_courses" (list of str)

    @note Returns a dictionary with None/empty values if the request fails
          or the page structure does not match expected patterns.
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
                    for cell in reversed(cells):
                        num = re.search(r"\b(\d+)\b", clean_text(cell.get_text()))
                        if num:
                            result["total_credits"] = int(num.group(1))
                            break

                # Course code cells
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
    """
    @brief Scrapes the QCC programs listing page and fetches details for each program.

    @details
    Sends a GET request to PROGRAMS_URL and parses the response to build an
    initial list of programs with their names, degree types, and URLs. Area of
    study is derived immediately from the URL via area_from_url(). Then iterates
    through each program, calls fetch_program_detail() to populate description,
    total_credits, and required_courses, and applies a 0.3 second polite delay
    between requests.

    The programs listing page uses <tr> table rows for individual program entries.
    The program name link is in the first cell and degree type is in the second cell.

    @return A list of program dictionaries with fields:
            name, area_of_study, degree_type, url, description,
            total_credits, required_courses, scraped_at.
    """
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
    """
    @brief Entry point — runs the programs scraper and saves results to JSON.

    @details
    Calls scrape_programs() to collect all program data, writes the results
    to qcc_programs.json, and prints a summary including total programs scraped,
    descriptions populated, total credits populated, area of study populated,
    and elapsed time.
    """
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