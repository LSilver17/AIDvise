# import dependencies
import sqlite3

try:
    # Connect to sqlite database
    conn = sqlite3.connect('Test.db')

    # Create a cursor object to execute SQL commands       
    cursor = conn.cursor()

    # Create the CourseInfo table and related tables if they do not exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Terms(
            TermID INTEGER PRIMARY KEY,
            Year INTEGER NOT NULL,
            Month TEXT NOT NULL,
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

    # Insert dummy test data (idempotent)
    cursor.executemany(
        '''
        INSERT OR IGNORE INTO Terms (TermID, Year, Month, Num)
        VALUES (?, ?, ?, ?)
        ''',
        [
            (1, 2026, 'January', 1),
            (2, 2026, 'May', 2),
            (3, 2026, 'August', 3),
        ],
    )

    cursor.executemany(
        '''
        INSERT OR IGNORE INTO CoursesOffered (CourseID, Department, Code, Description, Credits, TermID)
        VALUES (?, ?, ?, ?, ?, ?)
        ''',
        [
            (101, 'CSC', 212, 'Data Structures and Algorithms', 3, 1),
            (102, 'CSC', 251, 'Computer Organization and Architecture', 3, 1),
            (103, 'MTH', 231, 'Discrete Mathematics', 3, 1),
            (104, 'CSC', 310, 'Database Systems', 3, 2),
            (105, 'CSC', 340, 'Artificial Intelligence', 3, 3),
        ],
    )

    cursor.executemany(
        '''
        INSERT OR IGNORE INTO CourseRequirements (RequirementID, Department, Code, Grade, CourseID)
        VALUES (?, ?, ?, ?, ?)
        ''',
        [
            (201, 'CSC', 212, 2.0, 104),
            (202, 'MTH', 231, 2.0, 104),
            (203, 'CSC', 310, 2.0, 105),
        ],
    )

    cursor.executemany(
        '''
        INSERT OR IGNORE INTO Sections (SectionID, SectionNum, Instructor, MaxSeats, SeatsLeft, Modalim, Location, CourseID)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        [
            (301, 1, 'Dr. Patel', 30, 8, 'In-Person', 'Science Hall 210', 101),
            (302, 2, 'Prof. Nguyen', 25, 3, 'Hybrid', 'Engineering 115', 101),
            (303, 1, 'Dr. Lewis', 35, 11, 'Online', 'N/A', 104),
            (304, 1, 'Prof. Smith', 28, 5, 'In-Person', 'Tech Center 320', 105),
        ],
    )

    cursor.executemany(
        '''
        INSERT OR IGNORE INTO MeetTimes (MeetTimeID, Day, StartTime, EndTime, SectionID)
        VALUES (?, ?, ?, ?, ?)
        ''',
        [
            (401, 'Monday', '09:00', '10:15', 301),
            (402, 'Wednesday', '09:00', '10:15', 301),
            (403, 'Tuesday', '14:00', '15:15', 302),
            (404, 'Thursday', '14:00', '15:15', 302),
            (405, 'Wednesday', '18:00', '20:30', 304),
        ],
    )

    conn.commit()
    
except sqlite3.Error as e:
    # Handle any database errors
    print(f"An error occurred: {e}")
finally:
    # Ensure the connection is closed
    if conn:
        conn.close()