import sys, os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from database.database_dev_tools import __connect
import sqlite3

EVENTS = {
    "AI Career Panel": {
        "description": "Faculty and alumni discuss careers in AI and ML.",
        "dates": [
            {
                "date": "2027-04-20",
                "start_time": "14:00",
                "end_time": "15:30",
                "location": "Science Hall 220"
            },
            {
                "date": "2027-05-20",
                "start_time": "14:00",
                "end_time": "15:30",
                "location": "Science Hall 220"
            }
        ]
    },
    "Secure Coding Workshop": {
        "description": "Hands-on workshop covering secure coding practices.",
        "dates": [
            {
                "date": "2027-04-23",
                "start_time": "16:00",
                "end_time": "18:00",
                "location": "Tech Building 105"
            },
            {
                "date": "2027-05-23",
                "start_time": "16:00",
                "end_time": "18:00",
                "location": "Tech Building 105"
            }
        ]
    },
    "Software Design Interview Prep": {
        "description": "Interview prep focused on system design and collaboration.",
        "dates": [
            {
                "date": "2027-04-27",
                "start_time": "17:00",
                "end_time": "18:15",
                "location": "Career Center 101"
            },
            {
                "date": "2027-05-27",
                "start_time": "17:00",
                "end_time": "18:15",
                "location": "Career Center 101"
            }
        ]
    },
    "Poetry Open Mic": {
        "description": "Campus arts and literature open mic night.",
        "dates": [
            {
                "date": "2027-04-25",
                "start_time": "19:00",
                "end_time": "21:00",
                "location": "Student Union Lounge"
            },
            {
                "date": "2027-05-25",
                "start_time": "19:00",
                "end_time": "21:00",
                "location": "Student Union Lounge"
            }
        ]
    },
    "Beginner Pottery Class": {
        "description": "Introductory pottery wheel techniques.",
        "dates": [
            {
                "date": "2027-04-29",
                "start_time": "18:30",
                "end_time": "20:00",
                "location": "Arts Center Studio B"
            },
            {
                "date": "2027-05-29",
                "start_time": "18:30",
                "end_time": "20:00",
                "location": "Arts Center Studio B"
            }
        ]
    },
    "Intramural Soccer Tryouts": {
        "description": "Tryouts for spring intramural soccer teams.",
        "dates": [
            {
                "date": "2027-05-02",
                "start_time": "10:00",
                "end_time": "12:00",
                "location": "Rec Field North"
            },
            {
                "date": "2027-06-02",
                "start_time": "10:00",
                "end_time": "12:00",
                "location": "Rec Field North"
            }
        ]
    }
}

INTERESTS = [
    "Artificial Intelligence",
    "Software Engineering",
    "Cybersecurity",
]

# Utility function to insert dummy data for testing the event filtering graph
def insert_interest_dummy_data() -> None:
    with __connect() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR IGNORE INTO Students (
                Name,
                GPA,
                CreditsEarned,
                IntendedGraduationTerm,
                AdvisorID
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                "Jordan Reeves",
                3.42,
                57,
                "Spring 2027",
                None
            ),
        )
        student_id = cursor.lastrowid
          
        cursor.executemany(
            """
            INSERT OR IGNORE INTO Interests (Interest, ParentID)
            VALUES (?, ?)
            """,
            [(interest, student_id) for interest in INTERESTS],
        )
          
        cursor.executemany(
            """
            INSERT OR IGNORE INTO Events (Name, Description)
            VALUES (?, ?)
            """,
            [(event_name, event_info["description"]) for event_name, event_info in EVENTS.items()]
        )
        event_ids = {event_name: cursor.execute("SELECT ID FROM Events WHERE Name = ?", (event_name,)).fetchone()[0] for event_name in EVENTS.keys()}
     
        for event_name, event_info in EVENTS.items():
            for date_info in event_info["dates"]:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO EventDates (ParentID, Date, StartTime, EndTime, Location)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        event_ids[event_name],
                        date_info["date"],
                        date_info["start_time"],
                        date_info["end_time"],
                        date_info["location"]
                    )
                )

        conn.commit()


# Utility function to reset event check timestamps and relivent event table as well as move up event dates for testing purposes
def reset():
    with __connect() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE Students
            SET LastEventCheck = DATETIME('now', '-1 day')
            WHERE Name = ?
            """,
            ("Jordan Reeves",),
        )

        # update all event dates' year field to one year from now
        cursor.execute(
            """
            UPDATE EventDates
            SET Date = DATE(
                (CAST(STRFTIME('%Y', 'now') AS INTEGER) + 1) || '-' || STRFTIME('%m-%d', Date)
            ),
                TimeAdded = DATETIME('now')
            """
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
