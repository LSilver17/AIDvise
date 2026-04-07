import sys, os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from database.database_dev_tools import __connect
import sqlite3

DATABASE = "AlertTestDB.db"

# Utility function to insert dummy data for testing the event filtering graph
def insert_interest_dummy_data() -> None:
	with __connect(database=DATABASE) as conn:
		conn.execute("PRAGMA foreign_keys = ON")
		cursor = conn.cursor()
            
		cursor.execute(
			"""
			INSERT INTO Users (Username, Password, AccountType)
			VALUES (?, ?, ?)
			""",
			("dummy_student_01", "demo_password_hash", "student"),
		)
		user_id = cursor.lastrowid

		cursor.execute(
			"""
			INSERT INTO Students (
				Name,
				GPA,
				CreditsEarned,
				IntendedGraduationTerm,
				AdvisorID,
				ParentID
			)
			VALUES (?, ?, ?, ?, ?, ?)
			""",
			(
				"Jordan Reeves",
				3.42,
				57,
				"Spring 2027",
				None,
				user_id,
			),
		)
		student_id = cursor.lastrowid

		interests = [
			"Artificial Intelligence",
			"Software Engineering",
			"Cybersecurity",
		]
		cursor.executemany(
			"""
			INSERT INTO Interests (Interest, ParentID)
			VALUES (?, ?)
			""",
			[(interest, student_id) for interest in interests],
		)

		events = [
			(
				"AI Career Panel",
				"Faculty and alumni discuss careers in AI and ML.",
				"2027-04-20",
				"2027-04-20",
				"14:00",
				"15:30",
				"Science Hall 220",
			),
			(
				"Secure Coding Workshop",
				"Hands-on workshop covering secure coding practices.",
				"2027-04-23",
				"2027-04-23",
				"16:00",
				"18:00",
				"Tech Building 105",
			),
			(
				"Software Design Interview Prep",
				"Interview prep focused on system design and collaboration.",
				"2027-04-27",
				"2027-04-27",
				"17:00",
				"18:15",
				"Career Center 101",
			),
			(
				"Poetry Open Mic",
				"Campus arts and literature open mic night.",
				"2027-04-25",
				"2027-04-25",
				"19:00",
				"21:00",
				"Student Union Lounge",
			),
			(
				"Beginner Pottery Class",
				"Introductory pottery wheel techniques.",
				"2027-04-29",
				"2027-04-29",
				"18:30",
				"20:00",
				"Arts Center Studio B",
			),
			(
				"Intramural Soccer Tryouts",
				"Tryouts for spring intramural soccer teams.",
				"2027-05-02",
				"2027-05-02",
				"10:00",
				"12:00",
				"Rec Field North",
			),
		]
		cursor.executemany(
			"""
			INSERT INTO Events (
				Name,
				Description,
				StartDate,
				EndDate,
				StartTime,
				EndTime,
				Location
			)
			VALUES (?, ?, ?, ?, ?, ?, ?)
			""",
			events,
		)
            
		conn.commit()

# Utility function to reset event check timestamps and relivent event table as well as move up event dates for testing purposes
def reset():
    with __connect(database=DATABASE) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE Students
            SET LastEventCheck = NULL
            WHERE Name = ?
            """,
            ("Jordan Reeves",),
        )

        cursor.execute(
            """
            UPDATE Events
            SET StartDate = DATE('now', '+1 year', 'start of month', '+' || STRFTIME('%d', StartDate) || ' days' - 1),
                EndDate = DATE('now', '+1 year', 'start of month', '+' || STRFTIME('%d', EndDate) || ' days' - 1)
            WHERE Name IN (?, ?, ?, ?, ?, ?)
            """,
            (
                "AI Career Panel",
                "Secure Coding Workshop",
                "Software Design Interview Prep",
                "Poetry Open Mic",
                "Beginner Pottery Class",
                "Intramural Soccer Tryouts",
            ),
        )

        cursor.execute(
            """
            DELETE FROM RelevantEvents
            WHERE ParentID = (SELECT ID FROM Students WHERE Name = ?)
            """,
            ("Jordan Reeves",),
        )

        conn.commit()

if __name__ == "__main__":
    insert_interest_dummy_data()
