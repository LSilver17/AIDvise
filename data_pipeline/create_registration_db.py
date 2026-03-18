"""
create_registration_db.py
--------------------------
Creates a SQLite database from registration_sections.json.
Run this once to initialize the database.

USAGE:
    python create_registration_db.py
"""

import json
import sqlite3
import os

JSON_FILE = "registration_sections.json"
DB_FILE   = "registration.db"


def create_db(json_file: str, db_file: str):
    # Load JSON
    with open(json_file, "r", encoding="utf-8") as f:
        courses = json.load(f)

    print(f"Loaded {len(courses)} course sections from {json_file}")

    # Connect to SQLite (creates file if it doesn't exist)
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create table
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

        CREATE INDEX IF NOT EXISTS idx_department   ON courses(department);
        CREATE INDEX IF NOT EXISTS idx_course_code  ON courses(course_code);
        CREATE INDEX IF NOT EXISTS idx_status       ON courses(status);
        CREATE INDEX IF NOT EXISTS idx_instructor   ON courses(instructor);
    """)

    # Insert courses
    inserted = 0
    skipped  = 0

    for course in courses:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO courses (
                    course_code, department, course_number, section,
                    name, status, seats_open, seats_total, credits,
                    instructor, days_time, location, method,
                    begin_date, end_date, scraped_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            if cursor.rowcount > 0:
                inserted += 1
            else:
                skipped += 1
        except sqlite3.Error as e:
            print(f"  Error inserting {course.get('course_code')}: {e}")

    conn.commit()
    conn.close()

    print(f"✅ Database created: {db_file}")
    print(f"   Inserted: {inserted} courses")
    print(f"   Skipped:  {skipped} duplicates")


if __name__ == "__main__":
    if not os.path.exists(JSON_FILE):
        print(f"❌ {JSON_FILE} not found. Run scrape_registration_sections.py first.")
    else:
        create_db(JSON_FILE, DB_FILE)