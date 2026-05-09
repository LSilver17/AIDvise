# =============================================================================
# CSC 212 — AI Academic Advising Platform
# Data Pipeline

# Copyright (c) 2026 Quinsigamond Community College — CSC 212
# All rights reserved.

# Author:   Noel Mensah
# GitHub:   https://github.com/LSilver17/CSC212---AI-Agent

# =============================================================================

"""
@file scrape_catalog.py
@brief Scrapes the QCC course catalog from The Q portal for unique course details.

@details
This module uses Playwright to automate a headless Chromium browser and navigate
The Q portal's course search page. For each unique course code discovered across
all departments, it clicks into the course detail page and extracts:
    - Course name
    - Course description (with SQL apostrophe artifacts cleaned)
    - Credits
    - Prerequisites
    - Semesters offered

Only one section per unique base course code is scraped (e.g. ACC 101, not ACC 101-01
and ACC 101-02 separately), making this a catalog scraper rather than a section scraper.

@date 2026

@par Input
    The Q portal — live web scraping via Playwright

@par Output
    course_catalog.json — list of unique course dictionaries

@par Dependencies
    - playwright (pip install playwright && playwright install chromium)
    - beautifulsoup4
    - json (stdlib)
    - re (stdlib)
    - asyncio (stdlib)

@par Usage
    python scrape_catalog.py
"""

import json
import re
import asyncio
from datetime import datetime
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

## @brief URL of The Q portal's advanced course search page.
SEARCH_URL = "https://theq.qcc.edu/ICS/Course_Offerings_and_Schedule.jnz?portlet=AddDrop_Courses&screen=Advanced+Course+Search&screenType=next"

## @brief Academic term label to select from the portal dropdown.
TERM       = "Spring 2026"

## @brief Output path for the scraped catalog JSON file.
OUTPUT     = "course_catalog.json"

## @brief Whether to run the browser in headless (no UI) mode.
HEADLESS   = True


def clean_text(text):
    """
    @brief Removes excess whitespace from a string.

    @param text The raw string to clean.
    @return A normalized single-line string with no extra whitespace.
    """
    return " ".join(text.split()).strip()


def fix_apostrophes(text):
    """
    @brief Fixes SQL-escaped double apostrophes from The Q portal database.

    @details
    The Q portal stores course descriptions in a Jenzabar SQL database that
    escapes apostrophes as double apostrophes ('').  These artifacts bleed
    through into the scraped text (e.g. "company''s assets"). This function
    replaces all occurrences of '' with a single apostrophe.

    @param text The raw string potentially containing double apostrophes.
    @return The cleaned string with proper single apostrophes, or None if input is None.

    @par Example
    @code
    fix_apostrophes("company''s assets") -> "company's assets"
    fix_apostrophes(None)                -> None
    @endcode
    """
    if text:
        return text.replace("''", "'")
    return text


def parse_detail_page(html):
    """
    @brief Parses a course detail page from The Q portal and extracts course fields.

    @details
    The Q portal renders course details inside a span with id "pg0_V_lblCourseDescValue".
    The content is a mix of text nodes and <br> tags forming a block of labeled fields.

    Extraction strategy:
    - Course name: from the <h5> tag (format: "Course Name (DEPT NUM-SECTION)")
    - Description: all text lines before the "Credits:" label
    - Credits: regex match on "Credits: N" or "N Credits"
    - Prerequisites: regex match on "Prerequisites: ..." stopping before "Semester Offered"
    - Semesters offered: regex match on "Semester Offered: ..."

    Double apostrophes in description and prerequisites are cleaned via fix_apostrophes().

    @param html Raw HTML string of the course detail page.
    @return A dictionary with keys:
            - "name" (str or None)
            - "description" (str or None)
            - "credits" (str or None)
            - "prerequisites" (str or None)
            - "semesters_offered" (str or None)
    """
    soup = BeautifulSoup(html, "html.parser")
    result = {
        "name":              None,
        "description":       None,
        "credits":           None,
        "prerequisites":     None,
        "semesters_offered": None,
    }

    # Course name from the h5 tag (e.g. "Financial Accounting I (ACC 101-01)")
    h5 = soup.find("h5")
    if h5:
        name_text = clean_text(h5.get_text())
        name_match = re.match(r"^(.+?)\s*\([A-Z]", name_text)
        if name_match:
            result["name"] = name_match.group(1).strip()

    # Description span
    desc_span = soup.find("span", id="pg0_V_lblCourseDescValue")
    if not desc_span:
        return result

    # Get text lines split by <br> tags
    lines = []
    for item in desc_span.children:
        if hasattr(item, "get_text"):
            text = clean_text(item.get_text())
        else:
            text = clean_text(str(item))
        if text:
            lines.append(text)

    full = " ".join(lines)

    # Description = all lines before "Credits:"
    desc_lines = []
    for line in lines:
        if re.match(r"credits:", line, re.IGNORECASE):
            break
        desc_lines.append(line)
    if desc_lines:
        result["description"] = fix_apostrophes(" ".join(desc_lines))

    # Credits — match "Credits: 3" or "3 Credits" or "3 credit hours"
    credit_match = re.search(
        r"Credits?:\s*(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)\s*[Cc]redit",
        full
    )
    if credit_match:
        result["credits"] = credit_match.group(1) or credit_match.group(2)

    # Prerequisites — stop at Semester Offered or Credits
    prereq_match = re.search(
        r"Prerequisite[s]?:\s*(.+?)(?=\s*Semester Offered|\s*Credits?:|$)",
        full, re.IGNORECASE
    )
    if prereq_match:
        prereq = clean_text(prereq_match.group(1))
        if "semester offered" not in prereq.lower():
            result["prerequisites"] = fix_apostrophes(prereq)

    # Semesters offered — allow upper and lowercase, stop at Credits
    sem_match = re.search(
        r"Semester[s]? Offered:\s*([A-Za-z/,\s]+?)(?=\s*Credits?:|$)",
        full, re.IGNORECASE
    )
    if sem_match:
        result["semesters_offered"] = clean_text(sem_match.group(1))

    return result


async def get_search_results(page, dept_value, dept_label):
    """
    @brief Loads the search results page for a department and returns course section links.

    @details
    Navigates to the course search page, selects the given term and department,
    submits the search, and collects all course section links from the results table.
    Retries up to 3 times on failure with a 2-second delay between attempts.

    @param page The Playwright page object.
    @param dept_value The dropdown option value for the department.
    @param dept_label The human-readable department label (used for logging).
    @return A list of (section_code, href) tuples for all course links found,
            or an empty list if all attempts fail.
    """
    for attempt in range(3):
        try:
            await page.goto(SEARCH_URL, timeout=120000)
            await page.wait_for_load_state("networkidle", timeout=120000)
            await page.wait_for_selector("#pg0_V_ddlDept", timeout=60000)
            await page.select_option("#pg0_V_ddlTerm", label=TERM)
            await page.select_option("#pg0_V_ddlDept", value=dept_value)
            await page.click("#pg0_V_btnSearch")
            await page.wait_for_load_state("networkidle", timeout=120000)
            await page.wait_for_timeout(1500)

            course_links = await page.query_selector_all("table a")
            results = []
            for link in course_links:
                text = (await link.inner_text()).strip()
                href = await link.get_attribute("href") or ""
                if re.match(r"[A-Z]{2,4}\s+\d{3}-\w+", text) and "lnkCourse" in href:
                    results.append((text, href))
            return results
        except Exception as e:
            if attempt < 2:
                print(f"  ⚠ Retry {attempt+1}...")
                await asyncio.sleep(2)
            else:
                print(f"  ✗ Failed: {e}")
                return []


async def scrape_catalog():
    """
    @brief Asynchronously scrapes all unique courses from The Q portal catalog.

    @details
    Iterates through all departments on The Q portal. For each department,
    retrieves the list of course sections and identifies unique base course codes
    (e.g. "ACC 101" from "ACC 101-01"). For each unique code not yet scraped,
    navigates to the course detail page using a JavaScript postback and extracts
    course details via parse_detail_page().

    Courses already scraped in a previous department are skipped to avoid
    duplicates in the output catalog.

    @return A list of unique course dictionaries with fields:
            course_code, department, course_number, name, description,
            credits, prerequisites, semesters_offered, scraped_at.
    """
    catalog = {}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS)
        page = await browser.new_page()

        print("Loading QCC course search page...")
        await page.goto(SEARCH_URL, timeout=120000)
        await page.wait_for_load_state("networkidle", timeout=120000)

        # Get departments
        dept_select = await page.query_selector("#pg0_V_ddlDept")
        dept_options = await dept_select.query_selector_all("option")
        departments = []
        for opt in dept_options:
            value = await opt.get_attribute("value")
            label = (await opt.inner_text()).strip()
            if label.lower() != "all" and label:
                departments.append((value, label))

        print(f"Found {len(departments)} departments.\n")

        for dept_idx, (dept_value, dept_label) in enumerate(departments):
            print(f"[{dept_idx+1}/{len(departments)}] {dept_label}")

            course_links = await get_search_results(page, dept_value, dept_label)
            print(f"  Found {len(course_links)} sections")

            scraped_base = set()

            for section_code, href in course_links:
                base_match = re.match(r"([A-Z]{2,4}\s+\d+)", section_code)
                if not base_match:
                    continue
                base_code = base_match.group(1)

                if base_code in scraped_base or base_code in catalog:
                    scraped_base.add(base_code)
                    continue
                scraped_base.add(base_code)

                # Re-load search results before each course click
                course_links_fresh = await get_search_results(page, dept_value, dept_label)

                # Find this course's link in fresh results
                target_href = None
                for sc, href2 in course_links_fresh:
                    bm = re.match(r"([A-Z]{2,4}\s+\d+)", sc)
                    if bm and bm.group(1) == base_code:
                        target_href = href2
                        break

                if not target_href:
                    continue

                try:
                    postback_match = re.search(r"__doPostBack\('([^']+)'", target_href)
                    if not postback_match:
                        continue
                    target = postback_match.group(1)

                    await page.evaluate(f"__doPostBack('{target}', '')")
                    await page.wait_for_load_state("networkidle", timeout=30000)
                    try:
                        await page.wait_for_selector("#pg0_V_lblCourseDescValue", timeout=8000)
                    except Exception:
                        pass

                    html = await page.content()
                    detail = parse_detail_page(html)

                    dept_match = re.match(r"([A-Z]+)", base_code)
                    dept_code = dept_match.group(1) if dept_match else None
                    num_match = re.search(r"\d+", base_code)
                    course_num = num_match.group(0) if num_match else None

                    catalog[base_code] = {
                        "course_code":       base_code,
                        "department":        dept_code,
                        "course_number":     course_num,
                        "name":              detail["name"],
                        "description":       detail["description"],
                        "credits":           detail["credits"],
                        "prerequisites":     detail["prerequisites"],
                        "semesters_offered": detail["semesters_offered"],
                        "scraped_at":        datetime.now().isoformat(),
                    }

                    desc_preview = detail["description"][:60] if detail["description"] else "no description"
                    print(f"    ✓ {base_code} — {desc_preview}...")

                except Exception as e:
                    print(f"    ✗ Error on {base_code}: {e}")
                    continue

        await browser.close()

    return list(catalog.values())


async def main():
    """
    @brief Entry point — runs the catalog scraper and saves results to JSON.

    @details
    Calls scrape_catalog() to collect all unique course data, writes the
    results to course_catalog.json, and prints a summary including total
    courses scraped and elapsed time.
    """
    start = datetime.now()
    print("=" * 50)
    print("  QCC Course Catalog Scraper")
    print(f"  {start.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    courses = await scrape_catalog()

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(courses, f, indent=2)

    elapsed = (datetime.now() - start).seconds
    print(f"\n✅ Done in {elapsed}s")
    print(f"   Scraped {len(courses)} unique courses")
    print(f"   Saved to {OUTPUT}")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())