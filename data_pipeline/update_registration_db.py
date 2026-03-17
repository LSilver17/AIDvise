"""
update_registration_db.py
--------------------------
Efficiently updates the SQLite database from a freshly scraped
registration_sections.json. Uses UPSERT so existing records are
updated and new ones are inserted — no duplicates.

USAGE:
    1. Re-scrape:  python scrape_registration_sections.py
    2. Update DB:  python update_registration_db.py
"""

import json
import sqlite3
import os
from datetime import datetime

JSON_FILE = "registration_sections.json"
DB_FILE   = "registration.db"


def update_db(json_file: str, db_file: str):
    if not os.path.exists(db_file):
        print(f"❌ {db_file} not found. Run create_registration_db.py first.")
        return

    # Load fresh JSON
    with open(json_file, "r", encoding="utf-8") as f:
        courses = json.load(f)

    print(f"Loaded {len(courses)} course sections from {json_file}")

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    inserted = 0
    updated  = 0
    errors   = 0

    for course in courses:
        try:
            # UPSERT: insert new, or update all fields if course_code already exists
            cursor.execute("""
                INSERT INTO courses (
                    course_code, department, course_number, section,
                    name, status, seats_open, seats_total, credits,
                    instructor, days_time, location, method,
                    begin_date, end_date, scraped_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                course.get("course_code"),
                course.get("department"),
                course.get("course_number"),
                course.get("section"),
                course.get("name"),
                course.get("status"),
                course.get("seats_open"),
                course.get("seats_total"),
                course.get("credits"),
                course.get("instructor"),
                course.get("days_time"),
                course.get("location"),
                course.get("method"),
                course.get("begin_date"),
                course.get("end_date"),
                course.get("scraped_at"),
            ))

            # rowcount=1 means insert, rowcount=0 means no change needed
            if cursor.rowcount > 0:
                # Check if it was an insert or update
                cursor.execute("SELECT changes()")
                inserted += 1
            else:
                updated += 1

        except sqlite3.Error as e:
            print(f"  Error upserting {course.get('course_code')}: {e}")
            errors += 1

    conn.commit()

    # Summary
    total = cursor.execute("SELECT COUNT(*) FROM courses").fetchone()[0]
    conn.close()

    print(f"\n✅ Database updated: {db_file}")
    print(f"   Processed: {len(courses)} sections")
    print(f"   Total in DB: {total} courses")
    print(f"   Errors: {errors}")
    print(f"   Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    if not os.path.exists(JSON_FILE):
        print(f"❌ {JSON_FILE} not found. Run scrape_registration_sections.py first.")
    else:
        update_db(JSON_FILE, DB_FILE)