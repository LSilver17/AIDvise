# =============================================================================
# CSC 212 — AI Academic Advising Platform
# Data Pipeline 
#
# Copyright (c) 2026 Quinsigamond Community College — CSC 212
# All rights reserved.
#
# This source code is part of a student research project and may not be
# reproduced, distributed, or used without permission.
#
# Author:   Data Pipeline — CSC 212 AI Academic Advising Platform
# GitHub:   https://github.com/LSilver17/CSC212---AI-Agent
# Branch:   cws
# =============================================================================

"""
@file scrape_classes_page.py
@brief Scrapes the public QCC website for the full credit course listing with details.

@details
This module scrapes https://www.qcc.edu/classes for the complete list of QCC
credit courses, then visits each course's individual detail page to extract:
    - Description
    - Credits
    - Prerequisites
    - Semesters offered

Unlike scrape_catalog.py which uses Playwright to access The Q portal,
this scraper uses the Requests library and BeautifulSoup since the public
QCC website renders content statically (no JavaScript required).

Field extraction uses a line-scanning approach rather than CSS selectors,
because QCC's public pages present labeled fields as plain text rather than
structured HTML elements with identifying CSS classes.

@author Data Pipeline — CSC 212 AI Academic Advising Platform
@date 2026

@par Input
    https://www.qcc.edu/classes — public QCC course listing page

@par Output
    qcc_classes.json — list of course dictionaries with full detail fields

@par Dependencies
    - requests
    - beautifulsoup4
    - json (stdlib)
    - re (stdlib)
    - time (stdlib)

@par Usage
    python scrape_classes_page.py
"""

import json
import re
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime

## @brief Base URL for constructing absolute links from relative hrefs.
BASE_URL    = "https://www.qcc.edu"

## @brief URL of the QCC public classes listing page.
CLASSES_URL = "https://www.qcc.edu/classes"

## @brief Output path for the scraped JSON file.
OUTPUT      = "qcc_classes.json"

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


def fetch_course_detail(url):
    """
    @brief Fetches and extracts detail fields from a QCC course detail page.

    @details
    Sends an HTTP GET request to the course detail URL and parses the response
    using BeautifulSoup. Since QCC's course pages present fields as labeled
    plain text rather than structured HTML elements, this function splits the
    page's main content area into clean lines and scans for labeled field patterns.

    Extraction rules:
    - Credits: finds a line matching "Credits" then reads the numeric value on the next line
    - Semesters Offered: finds a line matching "Semester(s) Offered" then reads the next line
    - Prerequisites: finds a line matching "Prerequisites?" then reads the next line
    - Description: selects the longest text block over 80 characters that does not
      match navigation or label patterns

    A 0.3 second delay is applied between requests in scrape_classes() to avoid
    overloading QCC's server.

    @param url The full URL of the course detail page (e.g. https://www.qcc.edu/courses/financial-accounting-i).
    @return A dictionary with keys:
            - "description" (str or None)
            - "prerequisites" (str or None)
            - "credits" (str or None)
            - "semesters_offered" (str or None)

    @note Returns a dictionary with all None values if the request fails or
          the page structure does not match expected patterns.
    """
    result = {
        "description":       None,
        "prerequisites":     None,
        "credits":           None,
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
    """
    @brief Scrapes the QCC classes listing page and fetches details for each course.

    @details
    Sends a GET request to CLASSES_URL and parses the response to build an
    initial list of courses with their codes, names, and URLs. Then iterates
    through each course, calls fetch_course_detail() to populate the detail
    fields, and applies a 0.3 second polite delay between requests.

    The classes listing page uses <h2> tags for department headings and <tr>
    table rows for individual course entries. The course code is in the first
    cell and the course name link is in the second cell.

    @return A list of course dictionaries with fields:
            course_code, department, name, url, description,
            prerequisites, credits, semesters_offered, scraped_at.
    """
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
                "course_code":       code,
                "department":        current_dept,
                "name":              name,
                "url":               full_url,
                "description":       None,
                "prerequisites":     None,
                "credits":           None,
                "semesters_offered": None,
                "scraped_at":        datetime.now().isoformat(),
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
    """
    @brief Entry point — runs the classes scraper and saves results to JSON.

    @details
    Calls scrape_classes() to collect all course data, writes the results
    to qcc_classes.json, and prints a summary including total courses scraped,
    credits populated count, semesters offered populated count, and elapsed time.
    """
    start = datetime.now()
    print("=" * 50)
    print("  QCC Classes Page Scraper")
    print(f"  {start.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    courses = scrape_classes()

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(courses, f, indent=2)

    elapsed = (datetime.now() - start).seconds
    filled_credits   = sum(1 for c in courses if c["credits"] is not None)
    filled_semesters = sum(1 for c in courses if c["semesters_offered"] is not None)
    print(f"\n✅ Done in {elapsed}s")
    print(f"   Scraped {len(courses)} courses")
    print(f"   Credits populated:           {filled_credits}/{len(courses)}")
    print(f"   Semesters offered populated: {filled_semesters}/{len(courses)}")
    print(f"   Saved to {OUTPUT}")
    print("=" * 50)


if __name__ == "__main__":
    main()