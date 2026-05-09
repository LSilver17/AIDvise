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
@file refresh_registration.py
@brief Live scraper that refreshes QCC registration data from The Q portal.

@details
This module is the primary live scraping tool for the QCC registration data pipeline.
It uses Playwright to automate a headless Chromium browser, iterates through all
departments on The Q portal, scrapes all course sections for the current term,
saves the results to registration_sections.json, and upserts them into registration.db.

This script handles the full refresh cycle in three steps:
    1. Scrape all departments from The Q portal using Playwright
    2. Save results to registration_sections.json
    3. Upsert results into registration.db (insert new, update existing)

For parsing a pre-saved HTML snapshot instead of live scraping,
see scrape_registration_sections.py.

@author Data Pipeline — CSC 212 AI Academic Advising Platform
@date 2026

@par Configuration
    - SEARCH_URL : URL of The Q course offerings search page
    - TERM       : Academic term label to select (e.g. "Spring 2026")
    - JSON_FILE  : Output path for the JSON file
    - DB_FILE    : Path to the SQLite database file
    - HEADLESS   : Run browser in headless mode (True/False)

@par Dependencies
    - playwright (pip install playwright && playwright install chromium)
    - beautifulsoup4
    - sqlite3 (stdlib)
    - asyncio (stdlib)

@par Usage
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

## @brief URL of The Q portal's advanced course search page.
SEARCH_URL  = "https://theq.qcc.edu/ICS/Course_Offerings_and_Schedule.jnz?portlet=AddDrop_Courses&screen=Advanced+Course+Search&screenType=next"

## @brief Academic term label to select from the portal dropdown.
TERM        = "Spring 2026"

## @brief Output path for the scraped JSON file.
JSON_FILE   = "registration_sections.json"

## @brief Path to the SQLite database file.
DB_FILE     = "registration.db"

## @brief Whether to run the browser in headless (no UI) mode.
HEADLESS    = True


# ── Parsing helpers ───────────────────────────────────────

def clean_text(text):
    """
    @brief Removes excess whitespace from a string.

    @param text The raw string to clean.
    @return A normalized single-line string with no extra whitespace.

    @par Example
    @code
    clean_text("  ACC   101  ") -> "ACC 101"
    @endcode
    """
    return " ".join(text.split()).strip()


def parse_seats(s):
    """
    @brief Parses a seat availability string into open and total seat counts.

    @details
    Handles both standard slash "/" and Unicode division slash "∕" formats
    used by The Q portal (e.g. "1 / 24" or "1 ∕ 24").

    @param s The raw seats string from the registration table.
    @return A dictionary with keys "open" (int or None) and "total" (int or None).

    @par Example
    @code
    parse_seats("1 ∕ 24") -> {"open": 1, "total": 24}
    parse_seats("")        -> {"open": None, "total": None}
    @endcode
    """
    m = re.search("(\d+)\s*[/∕]\s*(\d+)", s)
    return {"open": int(m.group(1)), "total": int(m.group(2))} if m else {"open": None, "total": None}


def parse_details(s):
    """
    @brief Parses the details column into instructor, schedule, location, and method.

    @details
    The details column combines multiple fields into a slash-delimited string.
    Expected format: "Instructor / Days Time; Location / Method"

    @param s The raw details string from the registration table.
    @return A dictionary with keys:
            - "instructor" (str or None)
            - "days_time" (str or None): e.g. "MW 08:00-09:15AM"
            - "location" (str or None): e.g. "MAIN Campus, Room 312"
            - "method" (str or None): e.g. "Lecture"
    """
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
    """
    @brief Splits a full course code string into department, number, and section.

    @param code The full course code string (e.g. "ACC 101-01").
    @return A dictionary with keys "department", "number", and "section",
            all str or None if the format does not match.

    @par Example
    @code
    parse_course_code("ACC 101-01") -> {"department": "ACC", "number": "101", "section": "01"}
    @endcode
    """
    m = re.match("([A-Z]+)\s+(\d+)-(\w+)", code)
    return {"department": m.group(1), "number": m.group(2), "section": m.group(3)} if m else {"department": None, "number": None, "section": None}


def parse_html(html):
    """
    @brief Parses raw HTML from The Q portal and extracts course section data.

    @details
    Uses BeautifulSoup to find all table rows, identifies rows containing a
    valid course code (matching "DEPT NUM-SECTION"), and extracts all course
    fields using the confirmed 13-column layout of The Q portal.

    Column layout (auto-detected by course code position):
    - [idx+0] course_code
    - [idx+1] name
    - [idx+4] seats
    - [idx+5] status
    - [idx+6] details (instructor/schedule/method)
    - [idx+7] credits
    - [idx+8] begin_date
    - [idx+9] end_date

    @param html Raw HTML string from the browser page content.
    @return A list of course section dictionaries with all extracted fields.
    """
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
    """
    @brief Asynchronously scrapes all course sections from The Q portal.

    @details
    Launches a headless Chromium browser using Playwright, navigates to The Q
    portal's course search page, retrieves all department options from the
    dropdown, and iterates through each department to collect course sections.

    Each department is attempted up to 3 times with a 2-second delay between
    retries to handle intermittent portal timeouts.

    @return A list of all course section dictionaries scraped across all departments.

    @note Requires Playwright and Chromium to be installed:
          pip install playwright && playwright install chromium
    """
    all_courses = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS)
        page = await browser.new_page()

        print("Loading QCC course search page...")
        await page.goto(SEARCH_URL)
        await page.wait_for_load_state("networkidle")

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
    """
    @brief Creates or updates registration.db with the scraped course data.

    @details
    Connects to (or creates) the SQLite database at DB_FILE. Creates the
    courses table and indexes if they do not exist. Upserts each course
    record — inserting new records and updating existing ones on conflict
    with the unique course_code constraint.

    The following indexes are created for query performance:
    - idx_department  on courses(department)
    - idx_course_code on courses(course_code)
    - idx_status      on courses(status)
    - idx_instructor  on courses(instructor)

    @param courses A list of course section dictionaries to upsert.
    @return A tuple (inserted, errors, total) where:
            - inserted (int): number of records successfully processed
            - errors (int): number of records that failed
            - total (int): total records now in the database
    """
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
    """
    @brief Entry point — runs the full three-step registration refresh pipeline.

    @details
    Executes the pipeline in sequence:
        1. Scrapes all departments from The Q portal via scrape()
        2. Saves results to registration_sections.json
        3. Upserts results into registration.db via update_db()

    Prints a summary on completion including total sections scraped,
    database record count, error count, and elapsed time.
    """
    start = datetime.now()
    print("=" * 50)
    print("  QCC Registration Refresh")
    print(f"  {start.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    print("\n[1/3] Scraping QCC course offerings...")
    courses = await scrape()
    print(f"\n  Total scraped: {len(courses)} sections")

    print("\n[2/3] Saving to JSON...")
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(courses, f, indent=2)
    print(f"  Saved {len(courses)} sections to {JSON_FILE}")

    print("\n[3/3] Updating database...")
    inserted, errors, total = update_db(courses)
    print(f"  Processed: {len(courses)} | Total in DB: {total} | Errors: {errors}")

    elapsed = (datetime.now() - start).seconds
    print(f"\n✅ Done in {elapsed}s — {total} courses in database.")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())