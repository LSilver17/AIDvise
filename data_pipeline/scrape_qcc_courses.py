import requests
from bs4 import BeautifulSoup
from datetime import datetime


def clean_text(text: str) -> str:
    return " ".join(text.split()).strip()


def scrape_page(url: str, program_name: str, subject_hint: str = "") -> list[dict]:
    response = requests.get(url, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    rows = soup.select("table tr")

    courses = []

    for row in rows:
        cols = row.find_all(["td", "th"])

        if len(cols) < 5:
            continue

        values = [clean_text(col.get_text(" ", strip=True)) for col in cols]

        # Skip header rows
        joined = " | ".join(values).lower()
        if "course title" in joined and "course #" in joined:
            continue
        if "semester offered" in joined and "credits" in joined:
            continue

        title = values[0]
        course_code = values[1]
        semester_offered = values[2]
        credits = values[3]
        prerequisites = values[4]

        # Skip junk rows
        if not course_code or len(course_code) < 3:
            continue

        subject = subject_hint
        if " " in course_code:
            subject = course_code.split()[0]
        elif "-" in course_code:
            subject = course_code.split("-")[0]

        course = {
            "program_name": program_name,
            "subject": subject,
            "course_code": course_code,
            "title": title,
            "semester_offered": semester_offered,
            "credits": credits,
            "prerequisites": prerequisites,
            "source_url": url,
            "last_updated": datetime.now().isoformat()
        }

        courses.append(course)

    return courses


PROGRAM_PAGES = [
    {
        "program_name": "Respiratory Care",
        "url": "https://www.qcc.edu/healthcare/respiratory-care",
        "subject_hint": "RCP"
    },
    {
        "program_name": "Dental Hygiene",
        "url": "https://www.qcc.edu/healthcare/dental-hygiene",
        "subject_hint": "DEN"
    },
    {
        "program_name": "Early Childhood Education",
        "url": "https://www.qcc.edu/education-childcare/early-childhood-education",
        "subject_hint": "ECE"
    }
]


if __name__ == "__main__":
    all_courses = []

    for page in PROGRAM_PAGES:
        try:
            data = scrape_page(
                page["url"],
                page["program_name"],
                page["subject_hint"]
            )

            print(f"\n--- {page['program_name']} ---")
            for course in data[:5]:
                print(course)

            print(f"Total scraped from {page['program_name']}: {len(data)}")
            all_courses.extend(data)

        except Exception as e:
            print(f"Failed to scrape {page['program_name']}: {e}")

    print(f"\nGrand total courses scraped: {len(all_courses)}")

