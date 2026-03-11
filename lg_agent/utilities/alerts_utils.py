# import dependencies
import sqlite3

def get_events() -> list:
    """Returns a list of upcoming events."""
   
    conn = None

    try:
        # Connect to sqlite database
        conn = sqlite3.connect('Test.db')

        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        # Query for upcoming events
        cursor.execute(
            '''
            SELECT Name, Description, StartDate, EndDate, StartTime, EndTime, Location
            FROM Events
            WHERE StartDate >= DATE('now')
            ORDER BY StartDate ASC
            '''
        )

        # Fetch all results
        events = cursor.fetchall()

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
        conn = sqlite3.connect('Test.db')

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
        interests = cursor.fetchall()

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
        conn = sqlite3.connect('Test.db')

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
        relevant_events = cursor.fetchall()

        return relevant_events

    except Exception as exc:
        raise RuntimeError("Failed to fetch relevant events.") from exc
    finally:
        # Ensure the connection is closed
        if conn:
            conn.close()            