# import pytest
# import sqlite3
# import json
# import os
# import tempfile
# from datetime import datetime

# # ── Import functions from your scraper ───────────────────
# # Adjust the import path if needed
# import sys
# sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# from scrape_registration_sections import (
#     clean_text,
#     parse_seats,
#     parse_details,
#     parse_course_code,
# )


# # ── clean_text ────────────────────────────────────────────

# class TestCleanText:
#     def test_strips_whitespace(self):
#         assert clean_text("  hello  ") == "hello"

#     def test_collapses_multiple_spaces(self):
#         assert clean_text("hello   world") == "hello world"

#     def test_handles_newlines(self):
#         assert clean_text("hello\nworld") == "hello world"

#     def test_handles_tabs(self):
#         assert clean_text("hello\tworld") == "hello world"

#     def test_empty_string(self):
#         assert clean_text("") == ""

#     def test_already_clean(self):
#         assert clean_text("hello world") == "hello world"

#     def test_non_breaking_space(self):
#         result = clean_text("MW\xa008:00-09:15AM")
#         assert "\xa0" not in result


# # ── parse_seats ───────────────────────────────────────────

# class TestParseSeats:
#     def test_normal_seats(self):
#         result = parse_seats("1 ∕ 24")
#         assert result == {"open": 1, "total": 24}

#     def test_zero_open(self):
#         result = parse_seats("0 ∕ 20")
#         assert result == {"open": 0, "total": 20}

#     def test_full_seats(self):
#         result = parse_seats("24 ∕ 24")
#         assert result == {"open": 24, "total": 24}

#     def test_regular_slash(self):
#         result = parse_seats("5 / 30")
#         assert result == {"open": 5, "total": 30}

#     def test_no_spaces(self):
#         result = parse_seats("3/20")
#         assert result == {"open": 3, "total": 20}

#     def test_invalid_string(self):
#         result = parse_seats("N/A")
#         assert result == {"open": None, "total": None}

#     def test_empty_string(self):
#         result = parse_seats("")
#         assert result == {"open": None, "total": None}

#     def test_open_never_exceeds_total(self):
#         result = parse_seats("5 ∕ 24")
#         assert result["open"] <= result["total"]


# # ── parse_details ─────────────────────────────────────────

# class TestParseDetails:
#     def test_full_details(self):
#         s = "De Silva, Damindi / MW 08:00-09:15AM; MAIN Campus, Surprenant Hall, Computer Classroom, 312 / Lecture"
#         result = parse_details(s)
#         assert result["instructor"] == "De Silva, Damindi"
#         assert result["days_time"] == "MW 08:00-09:15AM"
#         assert "Surprenant Hall" in result["location"]
#         assert result["method"] == "Lecture"

#     def test_online_course(self):
#         s = "Smith, John / Online; Online Classes / Online Course"
#         result = parse_details(s)
#         assert result["instructor"] == "Smith, John"
#         assert result["method"] == "Online Course"

#     def test_in_person_blended(self):
#         s = "Rivas, Eduardo J. / T 11:00AM-12:15PM; MAIN Campus, Administration Building, Computer Classroom, 366 / In Person Blended"
#         result = parse_details(s)
#         assert result["instructor"] == "Rivas, Eduardo J."
#         assert result["days_time"] == "T 11:00AM-12:15PM"
#         assert result["method"] == "In Person Blended"

#     def test_empty_string(self):
#         result = parse_details("")
#         assert result["instructor"] == ""
#         assert result["days_time"] is None
#         assert result["location"] is None
#         assert result["method"] is None

#     def test_missing_location(self):
#         s = "Smith, John / MW 09:00-10:00AM / Lecture"
#         result = parse_details(s)
#         assert result["instructor"] == "Smith, John"
#         assert result["location"] is None


# # ── parse_course_code ─────────────────────────────────────

# class TestParseCourseCode:
#     def test_standard_code(self):
#         result = parse_course_code("ACC 101-01")
#         assert result == {"department": "ACC", "number": "101", "section": "01"}

#     def test_csc_code(self):
#         result = parse_course_code("CSC 212-03")
#         assert result == {"department": "CSC", "number": "212", "section": "03"}

#     def test_english_code(self):
#         result = parse_course_code("ENG 101-10")
#         assert result == {"department": "ENG", "number": "101", "section": "10"}

#     def test_four_letter_dept(self):
#         result = parse_course_code("MATH 201-01")
#         assert result["department"] == "MATH"

#     def test_invalid_code(self):
#         result = parse_course_code("not a code")
#         assert result == {"department": None, "number": None, "section": None}

#     def test_empty_string(self):
#         result = parse_course_code("")
#         assert result == {"department": None, "number": None, "section": None}

#     def test_department_is_uppercase(self):
#         result = parse_course_code("CSC 101-01")
#         assert result["department"] == result["department"].upper()


# # ── Database tests ────────────────────────────────────────

# class TestDatabase:
#     @pytest.fixture
#     def temp_db(self):
#         """Create a temporary database for testing."""
#         db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
#         db.close()
#         conn = sqlite3.connect(db.name)
#         conn.executescript("""
#             CREATE TABLE courses (
#                 id              INTEGER PRIMARY KEY AUTOINCREMENT,
#                 course_code     TEXT NOT NULL,
#                 department      TEXT,
#                 course_number   TEXT,
#                 section         TEXT,
#                 name            TEXT,
#                 status          TEXT,
#                 seats_open      INTEGER,
#                 seats_total     INTEGER,
#                 credits         TEXT,
#                 instructor      TEXT,
#                 days_time       TEXT,
#                 location        TEXT,
#                 method          TEXT,
#                 begin_date      TEXT,
#                 end_date        TEXT,
#                 scraped_at      TEXT,
#                 UNIQUE(course_code)
#             );
#         """)
#         conn.commit()
#         conn.close()
#         yield db.name
#         os.unlink(db.name)

#     @pytest.fixture
#     def sample_course(self):
#         return {
#             "course_code":   "CSC 101-01",
#             "department":    "CSC",
#             "course_number": "101",
#             "section":       "01",
#             "name":          "Intro to Computer Science",
#             "status":        "Open",
#             "seats_open":    5,
#             "seats_total":   24,
#             "credits":       "3.00",
#             "instructor":    "Chug, Rajesh",
#             "days_time":     "MW 09:30-10:45AM",
#             "location":      "MAIN Campus, Surprenant Hall, 210",
#             "method":        "Lecture",
#             "begin_date":    "01/26/2026",
#             "end_date":      "05/19/2026",
#             "scraped_at":    datetime.now().isoformat(),
#         }

#     def insert_course(self, db_path, course):
#         conn = sqlite3.connect(db_path)
#         conn.execute("""
#             INSERT OR IGNORE INTO courses (
#                 course_code, department, course_number, section,
#                 name, status, seats_open, seats_total, credits,
#                 instructor, days_time, location, method,
#                 begin_date, end_date, scraped_at
#             ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
#         """, tuple(course.values()))
#         conn.commit()
#         conn.close()

#     def test_insert_course(self, temp_db, sample_course):
#         self.insert_course(temp_db, sample_course)
#         conn = sqlite3.connect(temp_db)
#         row = conn.execute("SELECT * FROM courses WHERE course_code = 'CSC 101-01'").fetchone()
#         conn.close()
#         assert row is not None

#     def test_no_duplicates(self, temp_db, sample_course):
#         self.insert_course(temp_db, sample_course)
#         self.insert_course(temp_db, sample_course)
#         conn = sqlite3.connect(temp_db)
#         count = conn.execute("SELECT COUNT(*) FROM courses WHERE course_code = 'CSC 101-01'").fetchone()[0]
#         conn.close()
#         assert count == 1

#     def test_seats_stored_correctly(self, temp_db, sample_course):
#         self.insert_course(temp_db, sample_course)
#         conn = sqlite3.connect(temp_db)
#         row = conn.execute("SELECT seats_open, seats_total FROM courses WHERE course_code = 'CSC 101-01'").fetchone()
#         conn.close()
#         assert row[0] == 5
#         assert row[1] == 24

#     def test_upsert_updates_seats(self, temp_db, sample_course):
#         self.insert_course(temp_db, sample_course)
#         conn = sqlite3.connect(temp_db)
#         conn.execute("""
#             INSERT INTO courses (course_code, seats_open, seats_total)
#             VALUES (?, ?, ?)
#             ON CONFLICT(course_code) DO UPDATE SET
#                 seats_open = excluded.seats_open
#         """, ("CSC 101-01", 0, 24))
#         conn.commit()
#         row = conn.execute("SELECT seats_open FROM courses WHERE course_code = 'CSC 101-01'").fetchone()
#         conn.close()
#         assert row[0] == 0

#     def test_query_by_department(self, temp_db, sample_course):
#         self.insert_course(temp_db, sample_course)
#         conn = sqlite3.connect(temp_db)
#         rows = conn.execute("SELECT * FROM courses WHERE department = 'CSC'").fetchall()
#         conn.close()
#         assert len(rows) == 1

#     def test_query_open_courses(self, temp_db, sample_course):
#         self.insert_course(temp_db, sample_course)
#         conn = sqlite3.connect(temp_db)
#         rows = conn.execute("SELECT * FROM courses WHERE status = 'Open'").fetchall()
#         conn.close()
#         assert len(rows) == 1


# # ── JSON output tests ─────────────────────────────────────

# class TestJSONOutput:
#     @pytest.fixture
#     def sample_json(self, tmp_path):
#         data = [
#             {
#                 "course_code": "ACC 101-01",
#                 "department": "ACC",
#                 "course_number": "101",
#                 "section": "01",
#                 "name": "Financial Accounting I",
#                 "status": "Reopened",
#                 "seats_open": 1,
#                 "seats_total": 24,
#                 "credits": "3.00",
#                 "instructor": "De Silva, Damindi",
#                 "days_time": "MW 08:00-09:15AM",
#                 "location": "MAIN Campus, Surprenant Hall, 312",
#                 "method": "Lecture",
#                 "begin_date": "01/26/2026",
#                 "end_date": "05/19/2026",
#                 "scraped_at": datetime.now().isoformat(),
#             }
#         ]
#         f = tmp_path / "registration_sections.json"
#         f.write_text(json.dumps(data))
#         return str(f)

#     def test_json_is_valid(self, sample_json):
#         with open(sample_json) as f:
#             data = json.load(f)
#         assert isinstance(data, list)

#     def test_json_has_required_fields(self, sample_json):
#         with open(sample_json) as f:
#             data = json.load(f)
#         required = ["course_code", "department", "name", "status", "seats_open", "credits"]
#         for field in required:
#             assert field in data[0], f"Missing field: {field}"

#     def test_json_course_code_format(self, sample_json):
#         import re
#         with open(sample_json) as f:
#             data = json.load(f)
#         for course in data:
#             assert re.match(r"[A-Z]+ \d{3}-\w+", course["course_code"]), \
#                 f"Invalid course code format: {course['course_code']}"

#     def test_json_credits_are_numeric(self, sample_json):
#         with open(sample_json) as f:
#             data = json.load(f)
#         for course in data:
#             if course["credits"]:
#                 assert float(course["credits"]) > 0


# if __name__ == "__main__":
#     pytest.main([__file__, "-v"])
