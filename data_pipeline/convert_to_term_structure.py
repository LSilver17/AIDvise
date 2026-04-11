"""
convert_to_term_structure.py
-----------------------------
Converts registration_sections.json into the term data structure
requested by the backend team.

Input:  jsons/registration_sections.json
Output: jsons/term_data.json

USAGE:
    python convert_to_term_structure.py
"""

import json
import re
from datetime import datetime

INPUT  = "jsons/registration_sections.json"
OUTPUT = "jsons/term_data.json"


def get_term_info(begin_date_str):
    """Derive term Year, Season, and Num from a begin_date string (MM/DD/YYYY)."""
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
    Parse 'ACC 101-01' into:
      department = 'ACC'
      code       = 101
      section    = 1
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
    """Convert a value to int, return None if not possible."""
    try:
        return int(str(value).strip())
    except (ValueError, TypeError):
        return None


def convert(courses):
    # Group courses by term (derived from begin_date)
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