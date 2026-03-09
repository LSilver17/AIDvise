# import dependencies
import sqlite3

conn = None

try:
    # Connect to sqlite database
    conn = sqlite3.connect('Test.db')
    conn.execute('PRAGMA foreign_keys = ON')

    # Create a cursor object to execute SQL commands
    cursor = conn.cursor()

    # Create the course related tables if they do not exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Terms(
            TermID INTEGER PRIMARY KEY,
            Year INTEGER NOT NULL,
            Season TEXT NOT NULL,
            Num INTEGER
        )'''
    )
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS CoursesOffered(
            CourseID INTEGER PRIMARY KEY,
            Department TEXT NOT NULL,
            Code INTEGER NOT NULL,
            Description TEXT NOT NULL,
            Credits INTEGER NOT NULL,
            TermID INTEGER NOT NULL,
            FOREIGN KEY (TermID) REFERENCES Terms(TermID)
                ON DELETE CASCADE
        )'''
    )
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS CourseRequirements(
            RequirementID INTEGER PRIMARY KEY,
            Department TEXT NOT NULL,
            Code INTEGER,
            Grade REAL,
            CourseID INTEGER NOT NULL,
            FOREIGN KEY (CourseID) REFERENCES CoursesOffered(CourseID)
                ON DELETE CASCADE
        )'''
    )
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Sections(
            SectionID INTEGER PRIMARY KEY,
            SectionNum INTEGER NOT NULL,
            Instructor TEXT NOT NULL,
            MaxSeats INTEGER NOT NULL,
            SeatsLeft INTEGER NOT NULL,
            Modalim TEXT NOT NULL,
            Location TEXT,
            CourseID INTEGER NOT NULL,
            FOREIGN KEY (CourseID) REFERENCES CoursesOffered(CourseID)
                ON DELETE CASCADE
        )'''
    )
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS MeetTimes(
            MeetTimeID INTEGER PRIMARY KEY,
            Day TEXT NOT NULL,
            StartTime TEXT NOT NULL,
            EndTime TEXT NOT NULL,
            SectionID INTEGER NOT NULL,
            FOREIGN KEY (SectionID) REFERENCES Sections(SectionID)
                ON DELETE CASCADE
        )'''
    )

    # TODO: Create advisor related tables if they do not exist

    # TODO: Create student related tables if they do not exist

    # TODO: Create event related tables if they do not exist

    # Create user authentication table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users(
            UserID INTEGER PRIMARY KEY,
            Username TEXT NOT NULL UNIQUE,
            Password TEXT NOT NULL
        )'''
    )

    # Commit the changes to the database
    conn.commit()
    
except sqlite3.Error as e:
    raise RuntimeError(
        f"Database setup failed for 'Test.db': {e}. "
        "Check schema definitions, foreign key constraints, and seed data values."
    ) from e
except Exception as e:
    raise RuntimeError(
        f"Unexpected error while initializing 'Test.db': {e}"
    ) from e
finally:
    # Ensure the connection is closed
    if conn:
        conn.close()