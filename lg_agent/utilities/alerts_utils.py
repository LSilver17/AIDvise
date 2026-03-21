# import dependencies
import sqlite3

database = 'AdvisorDB.db'

def get_events() -> list:
    """Returns a list of upcoming events."""
   
    conn = None

    try:
        # Connect to sqlite database
        conn = sqlite3.connect(database)

        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        # Query for upcoming events
        cursor.execute(
            '''
            SELECT ID, Name, Description, StartDate, EndDate, StartTime, EndTime, Location
            FROM Events
            WHERE StartDate >= DATE('now')
            ORDER BY StartDate ASC
            '''
        )

        # Fetch all results
        events = [dict(ID=row[0], Name=row[1], Description=row[2], StartDate=row[3], EndDate=row[4], StartTime=row[5], EndTime=row[6], Location=row[7]) for row in cursor.fetchall()]

        return events

    except Exception as exc:
        raise RuntimeError("Failed to fetch upcoming events.") from exc
    finally:
        # Ensure the connection is closed
        if conn:
            conn.close()

def get_interests(userID: str) -> list:
    """Returns a list of the student's interests."""
   
    conn = None

    try:
        # Connect to sqlite database
        conn = sqlite3.connect(database)

        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        # Get studentID from userID
        cursor.execute(
            '''
            SELECT ID
            FROM Students
            WHERE UserID = ?
            ''',
            (userID,)
        )
        studentID = cursor.fetchone()

        # Query for the student's interests
        cursor.execute(
            '''
            SELECT Interest
            FROM Interests
            WHERE StudentID = ?
            ''',
            (studentID[0],)
        )

        # Fetch all results
        interests = [row[0] for row in cursor.fetchall()]

        return interests

    except Exception as exc:
        raise RuntimeError("Failed to fetch student interests.") from exc
    finally:
        # Ensure the connection is closed
        if conn:
            conn.close()

def get_relevant_events(userID: str) -> list:
    """Returns a list of relevant events for the student, sorted by urgency."""
   
    conn = None

    try:
        # Connect to sqlite database
        conn = sqlite3.connect(database)

        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        # Get studentID from userID
        cursor.execute(
            '''
            SELECT ID
            FROM Students
            WHERE UserID = ?
            ''',
            (userID,)
        )
        studentID = cursor.fetchone()

        # Query for relevant events, sorted by urgency
        cursor.execute(
            '''
            SELECT e.Name, e.Description, e.StartDate, e.EndDate, e.StartTime, e.EndTime, e.Location, r.Urgency
            FROM RelevantEvents r
            JOIN Events e ON r.EventID = e.ID
            WHERE r.StudentID = ?
            ORDER BY r.Urgency DESC, e.StartDate ASC
            ''',
            (studentID[0],)
        )

        # Fetch all results
        relevant_events = [dict(Name=row[0], Description=row[1], StartDate=row[2], EndDate=row[3], StartTime=row[4], EndTime=row[5], Location=row[6], Urgency=row[7]) for row in cursor.fetchall()]

        return relevant_events

    except Exception as exc:
        raise RuntimeError("Failed to fetch relevant events.") from exc
    finally:
        # Ensure the connection is closed
        if conn:
            conn.close()
