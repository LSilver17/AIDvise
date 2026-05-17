# =============================================================================
#
# Copyright 2026 
#
# Author:   Noel Mensah
# GitHub:   https://github.com/LSilver17/CSC212---AI-Agent
# 
# =============================================================================


"""
@file view_registration_db.py
@brief Interactive utility for querying and inspecting the registration database.

@details
This module provides an interactive command-line menu for exploring the
registration.db SQLite database. It is primarily used for testing and
verifying scraped data during development, and for ad-hoc querying of
course offerings without writing SQL directly.

Available operations:
    - Database summary (total sections, open/closed counts, department count)
    - List all departments with section counts
    - Search by department code
    - Show open/reopened courses (all departments or filtered by department)
    - Search by instructor last name
    - Search by delivery method (Lecture, Online, etc.)
    - Search by meeting days (MW, TR, MWF, etc.)
    - Export a department's courses to a JSON file

@author Data Pipeline — CSC 212 AI Academic Advising Platform
@date 2026

@par Input
    registration.db — SQLite database populated by create_registration_db.py
                      or refresh_registration.py

@par Dependencies
    - sqlite3 (stdlib)
    - json (stdlib)

@par Usage
    python view_registration_db.py

@note Run create_registration_db.py or refresh_registration.py first
      to populate registration.db before using this viewer.
"""

import sqlite3
import json

## @brief Path to the SQLite registration database file.
DB_FILE = "registration.db"


def get_connection():
    """
    @brief Opens and returns a connection to the registration database.

    @details
    Sets row_factory to sqlite3.Row so that query results can be accessed
    by column name (e.g. row['course_code']) in addition to by index.

    @return A sqlite3.Connection object connected to DB_FILE.
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def print_courses(rows, limit=10):
    """
    @brief Prints a formatted table of course rows to stdout.

    @details
    Displays each course as a single line with fixed-width columns showing
    course code, name, status, seat availability, and instructor.
    Output is truncated to the first `limit` rows.

    @param rows   An iterable of sqlite3.Row objects from a courses query.
    @param limit  Maximum number of rows to display (default 10).

    @par Example Output
    @code
    ACC 101-01     Financial Accounting I                   Reopened   1/24 seats  De Silva, Damindi
    @endcode
    """
    for row in list(rows)[:limit]:
        print(f"  {row['course_code']:<14} {row['name']:<40} {row['status']:<10} {row['seats_open']}/{row['seats_total']} seats  {row['instructor']}")


# ── Queries ───────────────────────────────────────────────

def summary():
    """
    @brief Prints a summary of the database contents.

    @details
    Queries the courses table for total section count, counts by status
    (Open, Reopened, Closed), and the number of distinct departments.
    Prints results to stdout.
    """
    conn = get_connection()
    total    = conn.execute("SELECT COUNT(*) FROM courses").fetchone()[0]
    open_    = conn.execute("SELECT COUNT(*) FROM courses WHERE status = 'Open'").fetchone()[0]
    reopened = conn.execute("SELECT COUNT(*) FROM courses WHERE status = 'Reopened'").fetchone()[0]
    closed   = conn.execute("SELECT COUNT(*) FROM courses WHERE status = 'Closed'").fetchone()[0]
    depts    = conn.execute("SELECT COUNT(DISTINCT department) FROM courses").fetchone()[0]
    conn.close()

    print("\n── Database Summary ──────────────────────────────")
    print(f"  Total sections : {total}")
    print(f"  Open           : {open_}")
    print(f"  Reopened       : {reopened}")
    print(f"  Closed         : {closed}")
    print(f"  Departments    : {depts}")


def list_departments():
    """
    @brief Lists all departments and their section counts in alphabetical order.

    @details
    Groups the courses table by department and counts sections per department.
    Results are sorted alphabetically by department code and printed to stdout.
    """
    conn = get_connection()
    rows = conn.execute("""
        SELECT department, COUNT(*) as count
        FROM courses
        GROUP BY department
        ORDER BY department
    """).fetchall()
    conn.close()

    print("\n── Departments ───────────────────────────────────")
    for row in rows:
        print(f"  {row['department']:<10} {row['count']} sections")


def search_by_department(dept: str):
    """
    @brief Searches and displays all course sections for a given department.

    @details
    Queries the courses table for all sections where department matches
    the given code (case-insensitive, converted to uppercase). Results
    are ordered by course number and section, and all matching rows are shown.

    @param dept The department code to search for (e.g. "CSC", "ENG", "MAT").
    """
    conn = get_connection()
    rows = conn.execute("""
        SELECT * FROM courses
        WHERE department = ?
        ORDER BY course_number, section
    """, (dept.upper(),)).fetchall()
    conn.close()

    print(f"\n── {dept.upper()} Courses ({len(rows)} sections) ──────────────────")
    print_courses(rows, limit=len(rows))


def search_open_courses(dept: str = None):
    """
    @brief Displays all open or reopened course sections, optionally filtered by department.

    @details
    Queries for courses with status "Open" or "Reopened". If a department
    code is provided, results are filtered to that department only.
    Displays up to 20 results.

    @param dept Optional department code to filter by (e.g. "CSC").
                If None, shows open courses across all departments.
    """
    conn = get_connection()
    if dept:
        rows = conn.execute("""
            SELECT * FROM courses
            WHERE status IN ('Open', 'Reopened') AND department = ?
            ORDER BY department, course_number
        """, (dept.upper(),)).fetchall()
    else:
        rows = conn.execute("""
            SELECT * FROM courses
            WHERE status IN ('Open', 'Reopened')
            ORDER BY department, course_number
        """).fetchall()
    conn.close()

    label = f"{dept.upper()} " if dept else ""
    print(f"\n── Open {label}Courses ({len(rows)} sections) ─────────────────")
    print_courses(rows, limit=20)


def search_by_instructor(name: str):
    """
    @brief Searches and displays all sections taught by a given instructor.

    @details
    Performs a case-insensitive partial match on the instructor field
    using SQL LIKE. Useful for finding all sections taught by a particular
    person when only their last name is known.

    @param name The instructor name or partial name to search for.
    """
    conn = get_connection()
    rows = conn.execute("""
        SELECT * FROM courses
        WHERE instructor LIKE ?
        ORDER BY course_code
    """, (f"%{name}%",)).fetchall()
    conn.close()

    print(f"\n── Courses by '{name}' ({len(rows)} sections) ────────────────")
    print_courses(rows, limit=len(rows))


def search_by_method(method: str):
    """
    @brief Searches and displays all sections with a given delivery method.

    @details
    Performs a partial match on the method field. Common values include:
    "Lecture", "Online Course", "Remote Learning", "In Person Blended", "Lab".
    Displays up to 20 results.

    @param method The delivery method string or partial string to search for.
    """
    conn = get_connection()
    rows = conn.execute("""
        SELECT * FROM courses
        WHERE method LIKE ?
        ORDER BY department, course_number
    """, (f"%{method}%",)).fetchall()
    conn.close()

    print(f"\n── '{method}' Courses ({len(rows)} sections) ──────────────────")
    print_courses(rows, limit=20)


def search_by_days(days: str):
    """
    @brief Searches and displays all sections meeting on given days.

    @details
    Performs a prefix match on the days_time field (e.g. "MW" matches
    "MW 08:00-09:15AM"). Common day patterns: MW, TR, MWF, F, S.
    Displays up to 20 results ordered by days_time and course code.

    @param days The day pattern to search for (e.g. "MW", "TR", "F").
    """
    conn = get_connection()
    rows = conn.execute("""
        SELECT * FROM courses
        WHERE days_time LIKE ?
        ORDER BY days_time, course_code
    """, (f"{days}%",)).fetchall()
    conn.close()

    print(f"\n── Courses on '{days}' ({len(rows)} sections) ────────────────")
    print_courses(rows, limit=20)


def export_department_json(dept: str):
    """
    @brief Exports all courses for a department to a JSON file.

    @details
    Queries all sections for the given department, converts each row to a
    dictionary, and writes the result to a JSON file named "{DEPT}_courses.json"
    in the current directory.

    @param dept The department code to export (e.g. "CSC").

    @par Side Effects
        Creates a file named "{dept.upper()}_courses.json" in the current directory.
    """
    conn = get_connection()
    rows = conn.execute("""
        SELECT * FROM courses WHERE department = ?
        ORDER BY course_number, section
    """, (dept.upper(),)).fetchall()
    conn.close()

    data = [dict(row) for row in rows]
    filename = f"{dept.upper()}_courses.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"\n✅ Exported {len(data)} {dept.upper()} courses to {filename}")


# ── Main Menu ─────────────────────────────────────────────

def main():
    """
    @brief Entry point — displays the interactive query menu and handles user input.

    @details
    Presents a numbered menu of query options in a loop until the user
    selects option 0 to exit. Each option prompts for any required input
    and calls the corresponding query function.

    Menu options:
        1. Database summary
        2. List all departments
        3. Search by department
        4. Show open courses (all or by dept)
        5. Search by instructor
        6. Search by delivery method
        7. Search by days (e.g. MW, TR, F)
        8. Export department to JSON
        0. Exit
    """
    print("\n╔══════════════════════════════════════╗")
    print("║   QCC Registration DB Viewer         ║")
    print("╚══════════════════════════════════════╝")

    while True:
        print("\n── Options ───────────────────────────────────────")
        print("  1. Database summary")
        print("  2. List all departments")
        print("  3. Search by department")
        print("  4. Show open courses (all or by dept)")
        print("  5. Search by instructor")
        print("  6. Search by delivery method")
        print("  7. Search by days (e.g. MW, TR, F)")
        print("  8. Export department to JSON")
        print("  0. Exit")

        choice = input("\nChoose an option: ").strip()

        if choice == "1":
            summary()
        elif choice == "2":
            list_departments()
        elif choice == "3":
            dept = input("Enter department code (e.g. CSC, ENG, MAT): ").strip()
            search_by_department(dept)
        elif choice == "4":
            dept = input("Enter department code (or press Enter for all): ").strip()
            search_open_courses(dept if dept else None)
        elif choice == "5":
            name = input("Enter instructor last name: ").strip()
            search_by_instructor(name)
        elif choice == "6":
            print("  Methods: Lecture, Online Course, Remote Learning, In Person Blended, Lab...")
            method = input("Enter method: ").strip()
            search_by_method(method)
        elif choice == "7":
            print("  Examples: MW, TR, MWF, F, S")
            days = input("Enter days: ").strip()
            search_by_days(days)
        elif choice == "8":
            dept = input("Enter department code to export: ").strip()
            export_department_json(dept)
        elif choice == "0":
            print("\nGoodbye!")
            break
        else:
            print("  Invalid option, try again.")


if __name__ == "__main__":
    main()