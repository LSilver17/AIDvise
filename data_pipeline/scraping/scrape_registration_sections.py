# =============================================================================
# CSC 212 — AI Academic Advising Platform
# Data Pipeline

# Copyright (c) 2026 Quinsigamond Community College — CSC 212
# All rights reserved.

# Author:   Noel Mensah
# GitHub:   https://github.com/LSilver17/CSC212---AI-Agent

# =============================================================================

"""
@file scrape_registration_sections.py
@brief Parses a locally saved HTML file of QCC's registration page into structured JSON.

@details
This module reads a saved HTML snapshot of The Q portal's course registration
page and extracts all course section data into a list of structured dictionaries.
The parsed data is saved to registration_sections.json.

This script does not perform live web requests — it parses a pre-saved HTML file.
For live scraping with automatic refresh, see refresh_registration.py.

@date 2026

@par Input
    saved_pages/registration_page.html — saved HTML snapshot of The Q portal

@par Output
    registration_sections.json — list of course section dictionaries

@par Dependencies
    - beautifulsoup4
    - json (stdlib)
    - re (stdlib)
    - datetime (stdlib)

@par Usage
    python scrape_registration_sections.py
"""

from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

## @brief Path to the locally saved HTML registration page.
HTML_FILE = "saved_pages/registration_page.html"


def clean_text(text: str) -> str:
    """
    @brief Removes excess whitespace from a string.

    @details
    Splits the input string on any whitespace, then rejoins with single spaces
    and strips leading/trailing whitespace. Handles newlines, tabs, and
    multiple consecutive spaces.

    @param text The raw string to clean.
    @return A normalized single-line string with no extra whitespace.

    @par Example
    @code
    clean_text("  ACC   101  ") -> "ACC 101"
    @endcode
    """
    return " ".join(text.split()).strip()


def parse_seats(seats_str: str) -> dict:
    """
    @brief Parses a seats string into open and total seat counts.

    @details
    The Q portal displays seat availability in the format "1 / 24" or "1 ∕ 24"
    (using either a standard slash or a Unicode division slash). This function
    extracts both numbers using a regex pattern that handles both slash variants.

    @param seats_str The raw seats string from the registration table (e.g. "1 / 24").
    @return A dictionary with keys:
            - "open" (int or None): number of open seats
            - "total" (int or None): total seats in the section

    @par Example
    @code
    parse_seats("1 ∕ 24") -> {"open": 1, "total": 24}
    parse_seats("")        -> {"open": None, "total": None}
    @endcode
    """
    match = re.search(r"(\d+)\s*[/∕]\s*(\d+)", seats_str)
    if match:
        return {"open": int(match.group(1)), "total": int(match.group(2))}
    return {"open": None, "total": None}


def parse_details(details_str: str) -> dict:
    """
    @brief Parses the details column into instructor, schedule, location, and method.

    @details
    The details column in The Q portal combines multiple fields into a single
    slash-delimited string with semicolons for sub-fields. The expected format is:
        "Instructor Name / Days Time; Location / Method"

    Parsing rules:
    - Part 0 (before first /): instructor name
    - Part 1 (between first and second /): days/time before semicolon, location after semicolon
    - Part 2 (after second /): delivery method (e.g. "Lecture", "Online")

    @param details_str The raw details string from the registration table.
    @return A dictionary with keys:
            - "instructor" (str or None)
            - "days_time" (str or None): e.g. "MW 08:00-09:15AM"
            - "location" (str or None): e.g. "MAIN Campus, Surprenant Hall, 312"
            - "method" (str or None): e.g. "Lecture"

    @par Example
    @code
    parse_details("De Silva, Damindi / MW 08:00-09:15AM; MAIN Campus, Room 312 / Lecture")
    # -> {"instructor": "De Silva, Damindi", "days_time": "MW 08:00-09:15AM",
    #     "location": "MAIN Campus, Room 312", "method": "Lecture"}
    @endcode
    """
    result = {"instructor": None, "days_time": None, "location": None, "method": None}
    parts = [p.strip() for p in details_str.split("/")]
    if len(parts) >= 1:
        result["instructor"] = clean_text(parts[0])
    if len(parts) >= 2:
        days_time_raw = parts[1].split(";")[0]
        result["days_time"] = clean_text(days_time_raw)
        if ";" in parts[1]:
            result["location"] = clean_text(parts[1].split(";")[1])
    if len(parts) >= 3:
        result["method"] = clean_text(parts[2])
    return result


def parse_course_code(code: str) -> dict:
    """
    @brief Splits a full course code string into department, number, and section.

    @details
    QCC course codes follow the format "DEPT NUM-SECTION" (e.g. "ACC 101-01").
    This function extracts each component using a regex match.

    @param code The full course code string (e.g. "ACC 101-01").
    @return A dictionary with keys:
            - "department" (str or None): e.g. "ACC"
            - "number" (str or None): e.g. "101"
            - "section" (str or None): e.g. "01"

    @par Example
    @code
    parse_course_code("ACC 101-01") -> {"department": "ACC", "number": "101", "section": "01"}
    parse_course_code("invalid")    -> {"department": None, "number": None, "section": None}
    @endcode
    """
    match = re.match(r"([A-Z]+)\s+(\d+)-(\w+)", code)
    if match:
        return {"department": match.group(1), "number": match.group(2), "section": match.group(3)}
    return {"department": None, "number": None, "section": None}


def parse_registration_html(file_path: str) -> list:
    """
    @brief Parses a saved HTML registration page and returns a list of course section dicts.

    @details
    Reads the HTML file at the given path, finds all table rows, and extracts
    course section data from rows that contain a valid course code (matching
    the pattern "DEPT NUM-SECTION"). Skips header rows and empty rows.

    The column layout detected from The Q portal is:
    - [idx+0] course_code   e.g. "ACC 101-01"
    - [idx+1] name          e.g. "Financial Accounting I"
    - [idx+2] req           (empty, skipped)
    - [idx+3] note          (empty, skipped)
    - [idx+4] seats         e.g. "1 ∕ 24"
    - [idx+5] status        e.g. "Reopened"
    - [idx+6] details       e.g. "Instructor / Days;Location / Method"
    - [idx+7] credits       e.g. "3.00"
    - [idx+8] begin_date    e.g. "01/26/2026"
    - [idx+9] end_date      e.g. "05/19/2026"

    @param file_path Path to the locally saved HTML file.
    @return A list of dictionaries, each representing one course section with keys:
            course_code, department, course_number, section, name, status,
            seats_open, seats_total, credits, instructor, days_time, location,
            method, begin_date, end_date, scraped_at.

    @throws FileNotFoundError if the HTML file does not exist at the given path.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    rows = soup.select("table tr")
    courses = []

    for row in rows:
        cols = row.find_all(["td", "th"])
        if len(cols) < 4:
            continue

        values = [clean_text(col.get_text(" ", strip=True)) for col in cols]

        # Skip header and empty rows
        joined = " | ".join(values).lower()
        if "course code" in joined and "name" in joined:
            continue
        if all(not v for v in values):
            continue

        # Find the course code column (e.g. "ACC 101-01")
        idx = None
        for i, v in enumerate(values):
            if re.match(r"[A-Z]{2,4}\s+\d{3}-\w+", v):
                idx = i
                break

        if idx is None:
            continue

        try:
            code_str   = values[idx]
            name       = values[idx + 1]
            seats_str  = values[idx + 4]
            status     = values[idx + 5]
            details    = values[idx + 6]
            credits    = values[idx + 7]
            begin_date = values[idx + 8] if len(values) > idx + 8 else None
            end_date   = values[idx + 9] if len(values) > idx + 9 else None
        except IndexError:
            continue

        seats      = parse_seats(seats_str)
        detail_map = parse_details(details)
        code_map   = parse_course_code(code_str)

        courses.append({
            "course_code":   code_str,
            "department":    code_map["department"],
            "course_number": code_map["number"],
            "section":       code_map["section"],
            "name":          name,
            "status":        status,
            "seats_open":    seats["open"],
            "seats_total":   seats["total"],
            "credits":       credits,
            "instructor":    detail_map["instructor"],
            "days_time":     detail_map["days_time"],
            "location":      detail_map["location"],
            "method":        detail_map["method"],
            "begin_date":    begin_date,
            "end_date":      end_date,
            "scraped_at":    datetime.now().isoformat(),
        })

    return courses


if __name__ == "__main__":
    data = parse_registration_html(HTML_FILE)

    print(f"Parsed {len(data)} course sections.\n")
    for course in data[:3]:
        print(json.dumps(course, indent=2))
        print("---")

    with open("registration_sections.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"\nSaved to registration_sections.json")