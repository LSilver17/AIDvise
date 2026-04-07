"""
scrape_catalog.py
------------------
Scrapes the QCC course catalog from The Q portal.
For each unique course, clicks into the detail page to extract:
  - Course name
  - Course description
  - Prerequisites
  - Semesters offered

Outputs: course_catalog.json

SETUP:
    pip install playwright beautifulsoup4
    playwright install chromium

USAGE:
    python scrape_catalog.py
"""

import json
import re
import asyncio
from datetime import datetime
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

SEARCH_URL = "https://theq.qcc.edu/ICS/Course_Offerings_and_Schedule.jnz?portlet=AddDrop_Courses&screen=Advanced+Course+Search&screenType=next"
TERM       = "Spring 2026"
OUTPUT     = "course_catalog.json"
HEADLESS   = True


def clean_text(text):
    return " ".join(text.split()).strip()


def parse_detail_page(html):
    soup = BeautifulSoup(html, "html.parser")
    result = {
        "name":              None,
        "description":       None,
        "prerequisites":     None,
        "semesters_offered": None,
    }

    # Course name from the h5 tag (e.g. "Financial Accounting I (ACC 101-01)")
    h5 = soup.find("h5")
    if h5:
        name_text = clean_text(h5.get_text())
        # Strip the "(ACC 101-01)" part
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

    # Description = all lines before "Credits:"
    desc_lines = []
    for line in lines:
        if line.lower().startswith("credits:"):
            break
        desc_lines.append(line)
    if desc_lines:
        result["description"] = " ".join(desc_lines)

    full = " ".join(lines)

    # Prerequisites — only if line starts with "Prerequisite"
    prereq_match = re.search(
        r"Prerequisite[s]?:\s*(.+?)(?:\s*Semester Offered|$)",
        full, re.IGNORECASE
    )
    if prereq_match:
        prereq = clean_text(prereq_match.group(1))
        # Exclude if it accidentally captured "Semester Offered"
        if "semester offered" not in prereq.lower():
            result["prerequisites"] = prereq

    # Semesters offered
    sem_match = re.search(r"Semester Offered:\s*([A-Z/,\s]+)", full)
    if sem_match:
        result["semesters_offered"] = clean_text(sem_match.group(1))

    return result


async def get_search_results(page, dept_value, dept_label):
    """Load search results for a department and return course links."""
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
                    except:
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