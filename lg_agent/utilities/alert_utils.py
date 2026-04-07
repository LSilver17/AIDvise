import sys, os

database_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database'))
if database_dir not in sys.path:
    sys.path.append(database_dir)

import datetime
import sqlite3
from data_pipeline.database.InterestDummies import __connect

DATABASE = "AdvisorDB.db"

# TODO: convert these to typescript and move to frontend

# Get student ID from username
def get_student_id(username: str, database: str = DATABASE) -> int:
    with __connect(database) as conn:
        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        # Get userID from username
        cursor.execute(
            '''
            SELECT ID
            FROM Users
            WHERE Username = ?
            ''',
            (username,)
        )
        userID = cursor.fetchone()

        # Get studentID from userID
        cursor.execute(
            '''
            SELECT ID
            FROM Students
            WHERE UserID = ?
            ''',
            (userID[0],)
        )
        student_id = cursor.fetchone()[0]

        return student_id

# Returns a list of relevant events for the student, sorted by urgency
def get_relevant_events(student_id: int, database: str = DATABASE) -> list[dict]:
    with __connect(database) as conn:
        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        # Query for relevant events, sorted by urgency
        cursor.execute(
            '''
            SELECT e.Name, e.Description, e.StartDate, e.EndDate, e.StartTime, e.EndTime, e.Location, r.Urgency
            FROM RelevantEvents r
            JOIN Events e ON r.EventID = e.ID
            WHERE r.StudentID = ?
            ORDER BY r.Urgency DESC, e.StartDate ASC
            ''',
            (student_id,)
        )

        # Fetch all results
        relevant_events = [dict(Name=row[0], Description=row[1], StartDate=row[2], EndDate=row[3], StartTime=row[4], EndTime=row[5], Location=row[6], Urgency=row[7]) for row in cursor.fetchall()]

        return relevant_events

# Returns a list of the sections the student is tracking for status change alerts.
def get_tracked_sections(student_id: int, database: str = DATABASE) -> list[str]:
    with __connect(database) as conn:
        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        # Query for the sections the student is tracking
        cursor.execute(
            '''
            SELECT SectionID
            FROM TrackedSections
            WHERE ParentID = ?
            ''',
            (student_id,)
        )

        # Fetch all results
        tracked_sections = [row[0] for row in cursor.fetchall()]

        return tracked_sections

# Returns a list of all new section status events for sections the student is tracking for course opening alerts since the last check.
def get_relevant_section_status_events(student_id: int, database: str = DATABASE) -> list[dict]:
    with __connect(database) as conn:
        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        # Get last status check time for student
        cursor.execute(
            '''
            SELECT LastStatusCheck
            FROM Students
            WHERE ID = ?
            ''',
            (student_id,)
        )
        last_status_check = cursor.fetchone()[0]

        # Update last status check time in database to now
        now = datetime.now().isoformat()
        cursor.execute(
            '''
            UPDATE Students
            SET LastStatusCheck = ?
            WHERE ID = ?
            ''',
            (now, student_id)
        )
        conn.commit()

        # Query for new section status events for tracked sections
        cursor.execute(
            '''
            SELECT s.SectionID, s.OldStatus, s.NewStatus, s.ChangeTime
            FROM SectionStatusEvents s
            JOIN TrackedSections t ON s.SectionID = t.SectionID
            WHERE t.ParentID = ? AND s.ChangeTime > ?
            ''',
            (student_id, last_status_check)
        )

        # Use section IDs to get course department/code and title as well as section number for each event
        section_status_events = []
        for row in cursor.fetchall():
            sectionID = row[0]
            old_status = row[1]
            new_status = row[2]
            change_time = row[3]

            cursor.execute(
                '''
                SELECT c.Department, c.Code, c.Title, s.SectionNumber
                FROM Sections s
                JOIN Courses c ON s.CourseID = c.ID
                WHERE s.ID = ?
                ''',
                (sectionID,)
            )
            section_info = cursor.fetchone()

            event = dict(Department=section_info[0], Code=section_info[1], Title=section_info[2], SectionNumber=section_info[3], OldStatus=old_status, NewStatus=new_status, ChangeTime=change_time)
            section_status_events.append(event)
        
        return section_status_events
