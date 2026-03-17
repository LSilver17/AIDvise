"""
refresh_registration.py
------------------------
One command to rule them all. Automatically:
  1. Opens the QCC course offerings page with Playwright
  2. Scrapes all departments
  3. Saves fresh registration_sections.json
  4. Updates registration.db

SETUP:
    pip install playwright beautifulsoup4
    playwright install chromium

USAGE:
    python refresh_registration.py
"""

import json
import re
import sqlite3
import asyncio
import os
from datetime import datetime
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

# ── Config ────────────────────────────────────────────────
SEARCH_URL  = "https://theq.qcc.edu/ICS/Course_Offerings_and_Schedule.jnz?portlet=AddDrop_Courses&screen=Advanced+Course+Search&screenType=next"
TERM        = "Spring 2026"
JSON_FILE   = "registration_sections.json"
DB_FILE     = "registration.db"
HEADLESS    = True
# ─────────────────────────────────────────────────────────


# ── Parsing helpers ───────────────────────────────────────

def clean_text(text):
    return " ".join(text.split()).strip()

def parse_seats(s):
    m = re.search(r"(\d+)\s*[/∕]\s*(\d+)", s)
    return {"open": int(m.group(1)), "total": int(m.group(2))} if m else {"open": None, "total": None}

def parse_details(s):
    result = {"instructor": None, "days_time": None, "location": None, "method": None}
    parts = [p.strip() for p in s.split("/")]
    if len(parts) >= 1:
        result["instructor"] = clean_text(parts[0])
    if len(parts) >= 2:
        result["days_time"] = clean_text(parts[1].split(";")[0])
        if ";" in parts[1]:
            result["location"] = clean_text(parts[1].split(";")[1])
    if len(parts) >= 3:
        result["method"] = clean_text(parts[2])
    return result

def parse_course_code(code):
    m = re.match(r"([A-Z]+)\s+(\d+)-(\w+)", code)
    return {"department": m.group(1), "number": m.group(2), "section": m.group(3)} if m else {"department": None, "number": None, "section": None}

def parse_html(html):
    soup = BeautifulSoup(html, "html.parser")
    courses = []
    for row in soup.select("table tr"):
        cols = row.find_all(["td", "th"])
        if len(cols) < 4:
            continue
        values = [clean_text(col.get_text(" ", strip=True)) for col in cols]
        joined = " | ".join(values).lower()
        if "course code" in joined and "name" in joined:
            continue
        if all(not v for v in values):
            continue
        idx = next((i for i, v in enumerate(values) if re.match(r"[A-Z]{2,4}\s+\d{3}-\w+", v)), None)
        if idx is None:
            continue
        try:
            code_str = values[idx]
            seats    = parse_seats(values[idx + 4])
            details  = parse_details(values[idx + 6])
            code_map = parse_course_code(code_str)
            courses.append({
                "course_code":   code_str,
                "department":    code_map["department"],
                "course_number": code_map["number"],
                "section":       code_map["section"],
                "name":          values[idx + 1],
                "status":        values[idx + 5],
                "seats_open":    seats["open"],
                "seats_total":   seats["total"],
                "credits":       values[idx + 7],
                "instructor":    details["instructor"],
                "days_time":     details["days_time"],
                "location":      details["location"],
                "method":        details["method"],
                "begin_date":    values[idx + 8] if len(values) > idx + 8 else None,
                "end_date":      values[idx + 9] if len(values) > idx + 9 else None,
                "scraped_at":    datetime.now().isoformat(),
            })
        except IndexError:
            continue
    return courses


# ── Scraper ───────────────────────────────────────────────

async def scrape():
    all_courses = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS)
        page = await browser.new_page()

        print("Loading QCC course search page...")
        await page.goto(SEARCH_URL)
        await page.wait_for_load_state("networkidle")

        # Get all department options using exact ID
        dept_select = await page.query_selector("#pg0_V_ddlDept")
        if not dept_select:
            print("❌ Could not find department dropdown. Check if page loaded correctly.")
            await browser.close()
            return []

        dept_options = await dept_select.query_selector_all("option")
        departments = []
        for opt in dept_options:
            value = await opt.get_attribute("value")
            label = (await opt.inner_text()).strip()
            if label.lower() != "all" and label:
                departments.append((value, label))

        print(f"Found {len(departments)} departments.\n")

        for i, (value, label) in enumerate(departments):
            print(f"[{i+1}/{len(departments)}] Scraping: {label}...")
            for attempt in range(3):
                try:
                    await page.goto(SEARCH_URL, timeout=60000)
                    await page.wait_for_load_state("networkidle", timeout=60000)
                    await page.wait_for_selector("#pg0_V_ddlDept", timeout=60000)
                    await page.select_option("#pg0_V_ddlTerm", label=TERM)
                    await page.select_option("#pg0_V_ddlDept", value=value)
                    await page.click("#pg0_V_btnSearch")
                    await page.wait_for_load_state("networkidle", timeout=60000)
                    courses = parse_html(await page.content())
                    all_courses.extend(courses)
                    print(f"  → {len(courses)} sections")
                    break
                except Exception as e:
                    if attempt < 2:
                        print(f"  ⚠ Attempt {attempt+1} failed, retrying...")
                        await asyncio.sleep(2)
                    else:
                        print(f"  ✗ Failed after 3 attempts: {e}")

        await browser.close()

    return all_courses


# ── Database update ───────────────────────────────────────

def update_db(courses):
    if not os.path.exists(DB_FILE):
        print(f"\n⚠️  {DB_FILE} not found — creating it now...")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS courses (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            course_code     TEXT NOT NULL,
            department      TEXT,
            course_number   TEXT,
            section         TEXT,
            name            TEXT,
            status          TEXT,
            seats_open      INTEGER,
            seats_total     INTEGER,
            credits         TEXT,
            instructor      TEXT,
            days_time       TEXT,
            location        TEXT,
            method          TEXT,
            begin_date      TEXT,
            end_date        TEXT,
            scraped_at      TEXT,
            UNIQUE(course_code)
        );
        CREATE INDEX IF NOT EXISTS idx_department  ON courses(department);
        CREATE INDEX IF NOT EXISTS idx_course_code ON courses(course_code);
        CREATE INDEX IF NOT EXISTS idx_status      ON courses(status);
        CREATE INDEX IF NOT EXISTS idx_instructor  ON courses(instructor);
    """)

    inserted = errors = 0
    for c in courses:
        try:
            cursor.execute("""
                INSERT INTO courses (
                    course_code, department, course_number, section,
                    name, status, seats_open, seats_total, credits,
                    instructor, days_time, location, method,
                    begin_date, end_date, scraped_at
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(course_code) DO UPDATE SET
                    status      = excluded.status,
                    seats_open  = excluded.seats_open,
                    seats_total = excluded.seats_total,
                    instructor  = excluded.instructor,
                    days_time   = excluded.days_time,
                    location    = excluded.location,
                    method      = excluded.method,
                    begin_date  = excluded.begin_date,
                    end_date    = excluded.end_date,
                    scraped_at  = excluded.scraped_at
            """, (
                c.get("course_code"), c.get("department"), c.get("course_number"),
                c.get("section"), c.get("name"), c.get("status"),
                c.get("seats_open"), c.get("seats_total"), c.get("credits"),
                c.get("instructor"), c.get("days_time"), c.get("location"),
                c.get("method"), c.get("begin_date"), c.get("end_date"),
                c.get("scraped_at"),
            ))
            inserted += 1
        except sqlite3.Error as e:
            print(f"  DB error for {c.get('course_code')}: {e}")
            errors += 1

    conn.commit()
    total = conn.execute("SELECT COUNT(*) FROM courses").fetchone()[0]
    conn.close()
    return inserted, errors, total


# ── Main ──────────────────────────────────────────────────

async def main():
    start = datetime.now()
    print("=" * 50)
    print("  QCC Registration Refresh")
    print(f"  {start.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    # Step 1: Scrape
    print("\n[1/3] Scraping QCC course offerings...")
    courses = await scrape()
    print(f"\n  Total scraped: {len(courses)} sections")

    # Step 2: Save JSON
    print("\n[2/3] Saving to JSON...")
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(courses, f, indent=2)
    print(f"  Saved {len(courses)} sections to {JSON_FILE}")

    # Step 3: Update DB
    print("\n[3/3] Updating database...")
    inserted, errors, total = update_db(courses)
    print(f"  Processed: {len(courses)} | Total in DB: {total} | Errors: {errors}")

    elapsed = (datetime.now() - start).seconds
    print(f"\n✅ Done in {elapsed}s — {total} courses in database.")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())