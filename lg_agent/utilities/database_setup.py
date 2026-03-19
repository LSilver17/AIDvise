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
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS Terms(
            ID INTEGER PRIMARY KEY,
            StartDate DATE NOT NULL,
            EndDate DATE NOT NULL,
            Year INTEGER NOT NULL,
            Season TEXT NOT NULL,
            Number INTEGER
        )'''
    )
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS CoursesOffered(
            ID INTEGER PRIMARY KEY,
            Department TEXT NOT NULL,
            Code INTEGER NOT NULL,
            Description TEXT NOT NULL,
            Credits INTEGER NOT NULL,
            TermID INTEGER NOT NULL,
            FOREIGN KEY (TermID) REFERENCES Terms(ID)
                ON DELETE CASCADE
        )'''
    )
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS CourseRequirements(
            ID INTEGER PRIMARY KEY,
            RequiredCourseID INTEGER NOT NULL,
            RequiredGrade REAL,
            CourseID INTEGER NOT NULL,
            FOREIGN KEY (CourseID) REFERENCES CoursesOffered(ID)
                ON DELETE CASCADE
        )'''
    )
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS Sections(
            ID INTEGER PRIMARY KEY,
            SectionNum INTEGER NOT NULL,
            Instructor TEXT NOT NULL,
            MaxSeats INTEGER NOT NULL,
            SeatsLeft INTEGER NOT NULL,
            Modality TEXT NOT NULL,
            Location TEXT,
            CourseID INTEGER NOT NULL,
            FOREIGN KEY (CourseID) REFERENCES CoursesOffered(ID)
                ON DELETE CASCADE
        )'''
    )
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS MeetTimes(
            ID INTEGER PRIMARY KEY,
            Day TEXT NOT NULL,
            StartTime TIME NOT NULL,
            EndTime TIME NOT NULL,
            SectionID INTEGER NOT NULL,
            FOREIGN KEY (SectionID) REFERENCES Sections(ID)
                ON DELETE CASCADE
        )'''
    )

    # Create user authentication table
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS Users(
            ID INTEGER PRIMARY KEY,
            Username TEXT NOT NULL UNIQUE,
            Password TEXT NOT NULL,
            AccountType TEXT NOT NULL
        )'''
    )

    # Create event related tables if they do not exist
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS Events(
            ID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL,
            Description TEXT NOT NULL,
            StartDate DATE NOT NULL,
            EndDate DATE NOT NULL,
            StartTime TIME NOT NULL,
            EndTime TIME NOT NULL,
            Location TEXT
        )'''
    )

    # Create advisor related tables if they do not exist TODO: decide what other info we should add to this
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS Advisors(
            ID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL,
            UserID INTEGER NOT NULL UNIQUE,
            FOREIGN KEY (UserID) REFERENCES Users(ID)
                ON DELETE CASCADE
        )'''
    )

    # Create student related tables if they do not exist
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS Students(
            ID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL,
            GPA REAL,
            CreditsEarned INTEGER,
            IntendedGraduationTerm TEXT,
            AdvisorID INTEGER,
            UserID INTEGER NOT NULL,
            FOREIGN KEY (AdvisorID) REFERENCES Advisors(ID)
                ON DELETE SET NULL,
            FOREIGN KEY (UserID) REFERENCES Users(ID)
                ON DELETE CASCADE
        )'''
    )
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS MajorsAndMinors(
            ID INTEGER PRIMARY KEY,
            Title TEXT NOT NULL,
            Type TEXT NOT NULL,
            StudentID INTEGER NOT NULL,
            FOREIGN KEY (StudentID) REFERENCES Students(ID)
                ON DELETE CASCADE
        )'''
    )
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS Interests(
            ID INTEGER PRIMARY KEY,
            Interest TEXT NOT NULL,
            StudentID INTEGER NOT NULL,
            FOREIGN KEY (StudentID) REFERENCES Students(ID)
                ON DELETE CASCADE
        )'''
    )
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS ChatLogs(
            ID INTEGER PRIMARY KEY,
            Log TEXT NOT NULL,
            Timestamp DATETIME NOT NULL,
            StudentID INTEGER NOT NULL,
            FOREIGN KEY (StudentID) REFERENCES Students(ID)
                ON DELETE CASCADE
        )'''
    )
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS RelevantEvents(
            ID INTEGER PRIMARY KEY,
            UrgencyLevel TEXT NOT NULL,
            EventID INTEGER NOT NULL,
            StudentID INTEGER NOT NULL,
            FOREIGN KEY (StudentID) REFERENCES Students(ID)
                ON DELETE CASCADE,
            FOREIGN KEY (EventID) REFERENCES Events(ID)
                ON DELETE CASCADE
        )'''
    )

    # Commit the changes to the database
    conn.commit()
    
except Exception as exc:
    raise RuntimeError("Failed to set up the database.") from exc
finally:
    # Ensure the connection is closed
    if conn:
        conn.close()