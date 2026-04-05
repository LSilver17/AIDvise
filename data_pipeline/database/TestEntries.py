import sqlite3
from datetime import datetime, timedelta
from database_dev_tools import setup_database, display_term_hierarchy

DATABASE = "TestDB.db"

def _connect() -> sqlite3.Connection:
	conn = sqlite3.connect(DATABASE)
	conn.execute("PRAGMA foreign_keys = ON")
	return conn

def _clear_existing_data(cursor: sqlite3.Cursor) -> None:
	# Child-to-parent delete order to satisfy foreign keys.
	delete_order = [
		"MajorMinorRequiredCourseOptions",
		"MajorMinorRequiredCourses",
		"MeetTimes",
		"Sections",
		"CoursesOffered",
		"CoursesTaken",
		"RelevantEvents",
		"ChatLogs",
		"Interests",
		"EventDates",
		"Students",
		"Advisors",
		"Users",
		"Events",
		"Terms",
		"MajorsAndMinors",
		"Courses",
	]
	for table in delete_order:
		cursor.execute(f"DELETE FROM {table}")

def seed_dummy_entries(reset_existing: bool = True) -> None:
	with _connect() as conn:
		
		cursor = conn.cursor()
		
		cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Courses'")
		if not cursor.fetchone():
			setup_database(database=DATABASE)
		
		if reset_existing:
			_clear_existing_data(cursor)

		# 1) Course catalog
		courses = [
			("CSC", 101, "Intro to Programming", "Fundamentals of programming with Python.", 3, "None"),
			("CSC", 212, "Data Structures and Algorithms", "Core data structures and algorithmic analysis.", 3, "CSC 101"),
			("CSC", 251, "Computer Organization", "Introduction to machine-level program execution.", 3, "CSC 101"),
			("CSC", 310, "Database Systems", "Relational models, SQL, and schema design.", 3, "CSC 212"),
			("CSC", 340, "Artificial Intelligence", "Foundational AI topics and search techniques.", 3, "CSC 212"),
			("MTH", 231, "Discrete Mathematics", "Logic, proofs, sets, relations, and combinatorics.", 3, "MTH 101"),
		]
		cursor.executemany(
			"""
			INSERT INTO Courses (Department, Code, Name, Description, Credits, Requirements)
			VALUES (?, ?, ?, ?, ?, ?)
			""",
			courses,
		)

		course_id_by_name = {
			row[0]: row[1]
			for row in cursor.execute("SELECT Name, ID FROM Courses").fetchall()
		}

		# 2) Major/Minor catalog
		major_minor_rows = [
			("Computer Science", "Focused study in software, systems, and theory.", 54, "Major"),
			("Mathematics", "Broad study in pure and applied mathematics.", 48, "Major"),
			("Data Science", "Minor emphasizing data analytics and modeling.", 18, "Minor"),
		]
		cursor.executemany(
			"""
			INSERT INTO MajorsAndMinors (Title, Description, CreditsRequired, Type)
			VALUES (?, ?, ?, ?)
			""",
			major_minor_rows,
		)

		major_minor_id_by_title = {
			row[0]: row[1]
			for row in cursor.execute("SELECT Title, ID FROM MajorsAndMinors").fetchall()
		}

		# 3) Major/Minor required-course groups and options
		requirement_groups = {
			"Computer Science": [
				["Intro to Programming"],
				["Data Structures and Algorithms"],
				["Computer Organization"],
				["Discrete Mathematics"],
				["Database Systems", "Artificial Intelligence"],
			],
			"Data Science": [
				["Discrete Mathematics"],
				["Database Systems", "Artificial Intelligence"],
			],
		}

		for title, options_per_group in requirement_groups.items():
			major_minor_id = major_minor_id_by_title[title]
			for option_group in options_per_group:
				cursor.execute(
					"INSERT INTO MajorMinorRequiredCourses (ParentID) VALUES (?)",
					(major_minor_id,),
				)
				required_group_id = cursor.lastrowid
				for course_name in option_group:
					cursor.execute(
						"""
						INSERT INTO MajorMinorRequiredCourseOptions (CourseID, ParentID)
						VALUES (?, ?)
						""",
						(course_id_by_name[course_name], required_group_id),
					)

		# 4) Terms and offerings
		terms = [
			(2026, "Spring", None),
			(2026, "Summer", 1),
			(2026, "Fall", None),
		]
		cursor.executemany(
			"INSERT INTO Terms (Year, Season, Number) VALUES (?, ?, ?)",
			terms,
		)

		term_ids = [row[0] for row in cursor.execute("SELECT ID FROM Terms ORDER BY ID").fetchall()]
		spring_term_id, summer1_term_id, fall_term_id = term_ids

		offerings = [
			(course_id_by_name["Intro to Programming"], spring_term_id),
			(course_id_by_name["Data Structures and Algorithms"], spring_term_id),
			(course_id_by_name["Discrete Mathematics"], spring_term_id),
			(course_id_by_name["Database Systems"], summer1_term_id),
			(course_id_by_name["Artificial Intelligence"], fall_term_id),
			(course_id_by_name["Computer Organization"], fall_term_id),
		]
		cursor.executemany(
			"INSERT INTO CoursesOffered (CourseID, ParentID) VALUES (?, ?)",
			offerings,
		)

		offered_course_ids = [
			row[0] for row in cursor.execute("SELECT ID FROM CoursesOffered ORDER BY ID").fetchall()
		]

		# 5) Sections and meet times
		sections = [
			(1, "Dr. Allen", "2026-01-12", "2026-05-01", "Open", 30, 8, "In Person", "Science Hall 201", offered_course_ids[0]),
			(1, "Prof. Nguyen", "2026-01-12", "2026-05-01", "Open", 28, 4, "Hybrid", "Tech Building 115", offered_course_ids[1]),
			(1, "Dr. Patel", "2026-01-12", "2026-05-01", "Closed", 25, 0, "In Person", "Math Center 302", offered_course_ids[2]),
			(1, "Dr. Rivera", "2026-05-18", "2026-07-10", "Reopened", 24, 5, "Online", "Online", offered_course_ids[3]),
			(1, "Dr. Carter", "2026-08-24", "2026-12-11", "Open", 35, 17, "In Person", "Engineering 101", offered_course_ids[4]),
			(2, "Dr. Lopez", "2026-08-24", "2026-12-11", "Open", 30, 9, "In Person", "Engineering 202", offered_course_ids[5]),
		]
		cursor.executemany(
			"""
			INSERT INTO Sections (
				SectionNum, Instructor, StartDate, EndDate, Status,
				MaxSeats, SeatsLeft, Method, Location, ParentID
			)
			VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
			""",
			sections,
		)

		section_ids = [row[0] for row in cursor.execute("SELECT ID FROM Sections ORDER BY ID").fetchall()]
		meet_times = [
			("Monday", "09:00", "10:15", section_ids[0]),
			("Wednesday", "09:00", "10:15", section_ids[0]),
			("Tuesday", "11:00", "12:15", section_ids[1]),
			("Thursday", "11:00", "12:15", section_ids[1]),
			("Monday", "13:00", "14:15", section_ids[2]),
			("Wednesday", "13:00", "14:15", section_ids[2]),
			("Tuesday", "18:00", "20:30", section_ids[3]),
			("Thursday", "18:00", "20:30", section_ids[3]),
			("Monday", "15:30", "16:45", section_ids[4]),
			("Wednesday", "15:30", "16:45", section_ids[4]),
			("Tuesday", "09:30", "10:45", section_ids[5]),
			("Thursday", "09:30", "10:45", section_ids[5]),
		]
		cursor.executemany(
			"INSERT INTO MeetTimes (Day, StartTime, EndTime, ParentID) VALUES (?, ?, ?, ?)",
			meet_times,
		)

		# 6) Users, advisors, students
		users = [
			("advisor_jkim", "pass123", "Advisor"),
			("advisor_mdiaz", "pass123", "Advisor"),
			("student_alice", "pass123", "Student"),
			("student_bob", "pass123", "Student"),
			("student_carla", "pass123", "Student"),
		]
		cursor.executemany(
			"INSERT INTO Users (Username, Password, AccountType) VALUES (?, ?, ?)",
			users,
		)

		user_id_by_username = {
			row[0]: row[1]
			for row in cursor.execute("SELECT Username, ID FROM Users").fetchall()
		}

		advisors = [
			("Dr. Jordan Kim", user_id_by_username["advisor_jkim"]),
			("Dr. Maria Diaz", user_id_by_username["advisor_mdiaz"]),
		]
		cursor.executemany(
			"INSERT INTO Advisors (Name, ParentID) VALUES (?, ?)",
			advisors,
		)

		advisor_ids = [row[0] for row in cursor.execute("SELECT ID FROM Advisors ORDER BY ID").fetchall()]

		students = [
			("Alice Johnson", 3.78, 46, "Fall 2027", advisor_ids[0], user_id_by_username["student_alice"]),
			("Bob Smith", 3.21, 61, "Spring 2027", advisor_ids[0], user_id_by_username["student_bob"]),
			("Carla Reyes", 3.92, 28, "Spring 2028", advisor_ids[1], user_id_by_username["student_carla"]),
		]
		cursor.executemany(
			"""
			INSERT INTO Students (
				Name, GPA, CreditsEarned, IntendedGraduationTerm, AdvisorID, ParentID
			)
			VALUES (?, ?, ?, ?, ?, ?)
			""",
			students,
		)

		student_ids = [row[0] for row in cursor.execute("SELECT ID FROM Students ORDER BY ID").fetchall()]

		# 7) Student-linked data
		interests = [
			("Machine Learning", student_ids[0]),
			("Backend Development", student_ids[0]),
			("Cybersecurity", student_ids[1]),
			("Data Visualization", student_ids[2]),
		]
		cursor.executemany(
			"INSERT INTO Interests (Interest, ParentID) VALUES (?, ?)",
			interests,
		)

		now = datetime.now()
		chat_logs = [
			("Can you help me plan next semester courses?", (now - timedelta(days=2)).isoformat(timespec="seconds"), student_ids[0]),
			("I need one more 300-level CSC course.", (now - timedelta(days=1)).isoformat(timespec="seconds"), student_ids[1]),
			("What internships are relevant to AI?", now.isoformat(timespec="seconds"), student_ids[2]),
		]
		cursor.executemany(
			"INSERT INTO ChatLogs (Log, Timestamp, ParentID) VALUES (?, ?, ?)",
			chat_logs,
		)

		courses_taken = [
			(course_id_by_name["Intro to Programming"], student_ids[0]),
			(course_id_by_name["Data Structures and Algorithms"], student_ids[0]),
			(course_id_by_name["Intro to Programming"], student_ids[1]),
			(course_id_by_name["Computer Organization"], student_ids[1]),
			(course_id_by_name["Intro to Programming"], student_ids[2]),
		]
		cursor.executemany(
			"INSERT INTO CoursesTaken (CourseID, ParentID) VALUES (?, ?)",
			courses_taken,
		)

		# 8) Events and event dates
		events = [
			("Resume Workshop", "Career center session for resume feedback."),
			("AI Industry Talk", "Guest speaker on applied AI systems."),
			("Internship Fair", "Networking with regional employers."),
		]
		cursor.executemany(
			"INSERT INTO Events (Name, Description) VALUES (?, ?)",
			events,
		)

		event_ids = [row[0] for row in cursor.execute("SELECT ID FROM Events ORDER BY ID").fetchall()]
		event_dates = [
			("2026-03-20", "15:00", "16:30", "Career Center 101", event_ids[0]),
			("2026-03-28", "13:00", "14:15", "Science Hall 220", event_ids[1]),
			("2026-04-05", "10:00", "14:00", "Student Union Ballroom", event_ids[2]),
		]
		cursor.executemany(
			"""
			INSERT INTO EventDates (Date, StartTime, EndTime, Location, ParentID)
			VALUES (?, ?, ?, ?, ?)
			""",
			event_dates,
		)

		relevant_events = [
			(1, event_ids[1], student_ids[0]),
			(2, event_ids[2], student_ids[1]),
			(1, event_ids[0], student_ids[2]),
		]
		cursor.executemany(
			"INSERT INTO RelevantEvents (Urgency, EventID, ParentID) VALUES (?, ?, ?)",
			relevant_events,
		)

		conn.commit()
		print("Dummy entries inserted successfully.")
		conn.close()

# For testing purposes, run this file to seed the database with dummy entries and display the term hierarchy to verify that the entries were added correctly.
if __name__ == "__main__":
	seed_dummy_entries(reset_existing=True)
	display_term_hierarchy(database=DATABASE)