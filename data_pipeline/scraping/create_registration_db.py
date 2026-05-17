# =============================================================================
#
# Copyright 2026 
#
# Author:   Noel Mensah
# GitHub:   https://github.com/LSilver17/CSC212---AI-Agent
# 
# =============================================================================

"""
@file create_registration_db.py
@brief Initializes the SQLite registration database from registration_sections.json.

@details
This module creates the registration.db SQLite database and populates it with
course section data from registration_sections.json. It is intended to be run
once to initialize the database. For subsequent refreshes (upsert on conflict),
use refresh_registration.py instead.

The database schema includes a UNIQUE constraint on course_code, so duplicate
entries are silently ignored (INSERT OR IGNORE). Four indexes are created for
fast querying by department, course code, status, and instructor.

Database schema:
@code
CREATE TABLE courses (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    course_code   TEXT NOT NULL UNIQUE,
    department    TEXT,
    course_number TEXT,
    section       TEXT,
    name          TEXT,
    status        TEXT,
    seats_open    INTEGER,
    seats_total   INTEGER,
    credits       TEXT,
    instructor    TEXT,
    days_time     TEXT,
    location      TEXT,
    method        TEXT,
    begin_date    TEXT,
    end_date      TEXT,
    scraped_at    TEXT
);
@endcode

@author Data Pipeline — CSC 212 AI Academic Advising Platform
@date 2026

@par Input
    registration_sections.json — scraped course section data

@par Output
    registration.db — initialized SQLite database

@par Dependencies
    - sqlite3 (stdlib)
    - json (stdlib)
    - os (stdlib)

@par Usage
    python create_registration_db.py

@note Run scrape_registration_sections.py or refresh_registration.py first
      to generate registration_sections.json before running this script.
"""

import json
import sqlite3
import os

## @brief Path to the input registration sections JSON file.
JSON_FILE = "registration_sections.json"

## @brief Path to the output SQLite database file.
DB_FILE   = "registration.db"


def create_db(json_file: str, db_file: str):
    """
    @brief Creates the SQLite database and populates it from the JSON file.

    @details
    Reads all course sections from the JSON file, connects to (or creates)
    the SQLite database at db_file, creates the courses table and indexes
    if they do not exist, and inserts all course records using INSERT OR IGNORE
    to skip duplicates based on the unique course_code constraint.

    Indexes created:
    - idx_department  on courses(department)
    - idx_course_code on courses(course_code)
    - idx_status      on courses(status)
    - idx_instructor  on courses(instructor)

    @param json_file Path to the registration_sections.json input file.
    @param db_file   Path to the SQLite database file to create or update.

    @par Side Effects
        Creates or modifies the SQLite database file at db_file.
        Prints a summary of inserted and skipped records on completion.

    @throws FileNotFoundError if json_file does not exist (handled by caller).
    @throws sqlite3.Error for individual record insert failures (logged, not raised).
    """
    # Load JSON
    with open(json_file, "r", encoding="utf-8") as f:
        courses = json.load(f)

    print(f"Loaded {len(courses)} course sections from {json_file}")

    # Connect to SQLite (creates file if it doesn't exist)
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create table and indexes
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