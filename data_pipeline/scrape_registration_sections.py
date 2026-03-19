from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

HTML_FILE = "saved_pages/registration_page.html"


def clean_text(text: str) -> str:
    return " ".join(text.split()).strip()


def parse_seats(seats_str: str) -> dict:
    match = re.search(r"(\d+)\s*[/∕]\s*(\d+)", seats_str)
    if match:
        return {"open": int(match.group(1)), "total": int(match.group(2))}
    return {"open": None, "total": None}


def parse_details(details_str: str) -> dict:
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
    match = re.match(r"([A-Z]+)\s+(\d+)-(\w+)", code)
    if match:
        return {"department": match.group(1), "number": match.group(2), "section": match.group(3)}
    return {"department": None, "number": None, "section": None}


def parse_registration_html(file_path: str) -> list[dict]:
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

        # Column layout (confirmed from debug output):
        # [idx+0] = course code
        # [idx+1] = name
        # [idx+2] = req (empty)
        # [idx+3] = note (empty)
        # [idx+4] = seats  e.g. "1 ∕ 24"
        # [idx+5] = status e.g. "Reopened"
        # [idx+6] = details (instructor / schedule / method)
        # [idx+7] = credits
        # [idx+8] = begin date
        # [idx+9] = end date
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