"""
view_registration_db.py
------------------------
A utility script to query and inspect the registration database.
Useful for testing data and exploring course offerings.

USAGE:
    python view_registration_db.py
"""

import sqlite3
import json

DB_FILE = "registration.db"


def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def print_courses(rows, limit=10):
    for row in list(rows)[:limit]:
        print(f"  {row['course_code']:<14} {row['name']:<40} {row['status']:<10} {row['seats_open']}/{row['seats_total']} seats  {row['instructor']}")


# ── Queries ───────────────────────────────────────────────

def summary():
    conn = get_connection()
    total      = conn.execute("SELECT COUNT(*) FROM courses").fetchone()[0]
    open_      = conn.execute("SELECT COUNT(*) FROM courses WHERE status = 'Open'").fetchone()[0]
    reopened   = conn.execute("SELECT COUNT(*) FROM courses WHERE status = 'Reopened'").fetchone()[0]
    closed     = conn.execute("SELECT COUNT(*) FROM courses WHERE status = 'Closed'").fetchone()[0]
    depts      = conn.execute("SELECT COUNT(DISTINCT department) FROM courses").fetchone()[0]
    conn.close()

    print("\n── Database Summary ──────────────────────────────")
    print(f"  Total sections : {total}")
    print(f"  Open           : {open_}")
    print(f"  Reopened       : {reopened}")
    print(f"  Closed         : {closed}")
    print(f"  Departments    : {depts}")


def list_departments():
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
