# =============================================================================
#
# Copyright 2026 
#
# Author:   Noel Mensah
# GitHub:   https://github.com/LSilver17/CSC212---AI-Agent
# 
# =============================================================================

"""
@file convert_to_term_structure.py
@brief Converts registration_sections.json into the backend team's term data structure.

@details
This module reads the raw registration data scraped from The Q portal and
converts it into the structured JSON format required by the backend LangGraph
advising agent. The output groups all course sections by academic term and
maps field names from the pipeline's snake_case convention to the backend
team's PascalCase schema.

The term (Year, Season, Num) is derived from each course's begin_date field
since The Q portal does not include an explicit term label in its course records.

Backend team's required schema:
@code
{
  "Year": int,
  "Season": str,
  "Num": int,
  "CoursesOffered": [
    {
      "Department": str,
      "Code": int,
      "SectionNum": int,
      "Instructor": str,
      "StartDate": str,
      "EndDate": str,
      "Status": str,
      "MaxSeats": int,
      "SeatsLeft": int,
      "Method": str,
      "Location": str,
      "MeetTimes": str
    }
  ]
}
@endcode

@date 2026

@par Input
    jsons/registration_sections.json — raw scraped registration data

@par Output
    jsons/term_data.json — term-structured data in backend schema

@par Dependencies
    - json (stdlib)
    - re (stdlib)
    - datetime (stdlib)

@par Usage
    python convert_to_term_structure.py
"""

import json
import re
from datetime import datetime

## @brief Path to the input registration sections JSON file.
INPUT  = "jsons/registration_sections.json"

## @brief Path to the output term data JSON file.
OUTPUT = "jsons/term_data.json"


def get_term_info(begin_date_str):
    """
    @brief Derives academic term Year, Season, and Num from a begin_date string.

    @details
    Since The Q portal does not include an explicit term field in its course
    records, the term is derived from the begin_date using month-based mapping:
        - January–April  → Spring (Num = 1)
        - May–July       → Summer (Num = 2)
        - August–December → Fall  (Num = 3)

    @param begin_date_str The begin date string in MM/DD/YYYY format
                          (e.g. "01/26/2026").
    @return A tuple (year, season, num) where:
            - year (int or None): the calendar year
            - season (str or None): "Spring", "Summer", or "Fall"
            - num (int or None): term number (1, 2, or 3)
            Returns (None, None, None) if the date string cannot be parsed.

    @par Example
    @code
    get_term_info("01/26/2026") -> (2026, "Spring", 1)
    get_term_info("08/01/2026") -> (2026, "Fall", 3)
    get_term_info("")           -> (None, None, None)
    @endcode
    """
    try:
        date = datetime.strptime(begin_date_str, "%m/%d/%Y")
    except (ValueError, TypeError):
        return None, None, None

    year  = date.year
    month = date.month

    if month in (1, 2, 3, 4):
        season = "Spring"
        num    = 1
    elif month in (5, 6, 7):
        season = "Summer"
        num    = 2
    else:                      # 8-12
        season = "Fall"
        num    = 3

    return year, season, num


def parse_course_code(course_code):
    """
    @brief Parses a full course code string into department, code number, and section number.

    @details
    QCC course codes follow the format "DEPT NUM-SECTION" (e.g. "ACC 101-01").
    The section is stripped of leading zeros and converted to an integer.
    If the section contains non-numeric characters, section_num defaults to 0.

    @param course_code The full course code string (e.g. "ACC 101-01").
    @return A tuple (department, code, section_num) where:
            - department (str or None): e.g. "ACC"
            - code (int or None): e.g. 101
            - section_num (int or None): e.g. 1 (from "01")
            Returns (None, None, None) if the format does not match.

    @par Example
    @code
    parse_course_code("ACC 101-01") -> ("ACC", 101, 1)
    parse_course_code("ENG 102-10") -> ("ENG", 102, 10)
    parse_course_code("invalid")    -> (None, None, None)
    @endcode
    """
    match = re.match(r"([A-Z]+)\s+(\d+)(?:-(\w+))?", course_code.strip())
    if not match:
        return None, None, None
    department  = match.group(1)
    code        = int(match.group(2))
    section_raw = match.group(3) or "0"
    try:
        section_num = int(section_raw.lstrip("0") or "0")
    except ValueError:
        section_num = 0
    return department, code, section_num


def safe_int(value):
    """
    @brief Safely converts a value to int, returning None on failure.

    @details
    Handles string inputs by stripping whitespace before conversion.
    Used to convert seats_total and seats_open fields which may be
    stored as strings in the source JSON.

    @param value The value to convert (str, int, float, or None).
    @return The integer value, or None if conversion is not possible.

    @par Example
    @code
    safe_int("24")  -> 24
    safe_int(None)  -> None
    safe_int("N/A") -> None
    @endcode
    """
    try:
        return int(str(value).strip())
    except (ValueError, TypeError):
        return None


def convert(courses):
    """
    @brief Converts a flat list of course sections into term-grouped backend schema.

    @details
    Groups all course sections by academic term using get_term_info() on each
    course's begin_date. For each unique term encountered, creates a term
    dictionary with Year, Season, Num, and CoursesOffered. Each course section
    is mapped from the pipeline's field names to the backend team's PascalCase
    schema and appended to the appropriate term's CoursesOffered list.

    Field mapping:
    - department       → Department
    - course_number    → Code (as int)
    - section          → SectionNum (as int, leading zeros stripped)
    - instructor       → Instructor
    - begin_date       → StartDate
    - end_date         → EndDate
    - status           → Status
    - seats_total      → MaxSeats (as int)
    - seats_open       → SeatsLeft (as int)
    - method           → Method
    - location         → Location
    - days_time        → MeetTimes

    @param courses A list of course section dictionaries from registration_sections.json.
    @return A list of term dictionaries matching the backend team's required schema.
    """
    terms = {}

    for course in courses:
        begin_date = course.get("begin_date", "")
        year, season, num = get_term_info(begin_date)

        term_key = f"{season} {year}"
        if term_key not in terms:
            terms[term_key] = {
                "Year":           year,
                "Season":         season,
                "Num":            num,
                "CoursesOffered": []
            }

        department, code, section_num = parse_course_code(
            course.get("course_code", "")
        )

        entry = {
            "Department": department,
            "Code":        code,
            "SectionNum":  section_num,
            "Instructor":  course.get("instructor") or None,
            "StartDate":   course.get("begin_date") or None,
            "EndDate":     course.get("end_date") or None,
            "Status":      course.get("status") or None,
            "MaxSeats":    safe_int(course.get("seats_total")),
            "SeatsLeft":   safe_int(course.get("seats_open")),
            "Method":      course.get("method") or None,
            "Location":    course.get("location") or None,
            "MeetTimes":   course.get("days_time") or None,
        }

        terms[term_key]["CoursesOffered"].append(entry)

    return list(terms.values())


def main():
    """
    @brief Entry point — runs the conversion and saves the term-structured JSON.

    @details
    Loads registration_sections.json, calls convert() to transform it into
    the backend schema, writes the result to term_data.json, and prints a
    summary showing the number of terms and courses per term.
    """
    print("=" * 50)
    print("  Registration → Term Structure Converter")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    with open(INPUT, "r", encoding="utf-8") as f:
        courses = json.load(f)

    print(f"Loaded {len(courses)} course sections from {INPUT}")

    term_data = convert(courses)

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(term_data, f, indent=2)

    total_courses = sum(len(t["CoursesOffered"]) for t in term_data)
    print(f"Converted into {len(term_data)} term(s)")
    print(f"Total course entries: {total_courses}")
    for t in term_data:
        print(f"  {t['Season']} {t['Year']} (Num={t['Num']}): {len(t['CoursesOffered'])} courses")
    print(f"Saved to {OUTPUT}")
    print("=" * 50)


if __name__ == "__main__":
    main()