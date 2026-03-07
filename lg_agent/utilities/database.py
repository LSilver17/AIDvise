# import dependencies
import sqlite3

conn = None

try:
    # Connect to sqlite database
    conn = sqlite3.connect('Test.db')
    conn.execute('PRAGMA foreign_keys = ON')

    # Create a cursor object to execute SQL commands       
    cursor = conn.cursor()

    # Create the CourseInfo table and related tables if they do not exist
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

    # Insert dummy test data (idempotent)
    cursor.executemany(
        '''
        INSERT OR IGNORE INTO Terms (TermID, Year, Season, Num)
        VALUES (?, ?, ?, ?)
        ''',
        [
            (1, 2026, 'Spring', None),
            (2, 2026, 'Fall', None),
            (3, 2026, 'Summer', 1),
            (4, 2026, 'Summer', 2),
        ],
    )

    cursor.executemany(
        '''
        INSERT OR IGNORE INTO CoursesOffered (CourseID, Department, Code, Description, Credits, TermID)
        VALUES (?, ?, ?, ?, ?, ?)
        ''',
        [
            (1, 'CSC', 212, 'Data Structures and Algorithms', 3, 1),
            (2, 'CSC', 251, 'Computer Organization and Architecture', 3, 1),
            (3, 'MTH', 231, 'Discrete Mathematics', 3, 1)
        ],
    )

    cursor.executemany(
        '''
        INSERT OR IGNORE INTO CoursesOffered (CourseID, Department, Code, Description, Credits, TermID)
        VALUES (?, ?, ?, ?, ?, ?)
        ''',
        [
            (4, 'CSC', 310, 'Database Systems', 3, 2),
            (5, 'CSC', 340, 'Artificial Intelligence', 3, 2),
            (6, 'CSC', 450, 'Software Engineering', 3, 2)
        ],
    )

    cursor.executemany(
        '''
        INSERT OR IGNORE INTO CoursesOffered (CourseID, Department, Code, Description, Credits, TermID)
        VALUES (?, ?, ?, ?, ?, ?)
        ''',
        [
            (7, 'CSC', 212, 'Data Structures and Algorithms', 3, 3),
            (8, 'CSC', 251, 'Computer Organization and Architecture', 3, 3),
            (9, 'MTH', 231, 'Discrete Mathematics', 3, 3)
        ],
    )

    cursor.executemany(
        '''
        INSERT OR IGNORE INTO CoursesOffered (CourseID, Department, Code, Description, Credits, TermID)
        VALUES (?, ?, ?, ?, ?, ?)
        ''',
        [
            (10, 'CSC', 212, 'Data Structures and Algorithms', 3, 4),
            (11, 'CSC', 251, 'Computer Organization and Architecture', 3, 4),
            (12, 'MTH', 231, 'Discrete Mathematics', 3, 4)
        ],
    )

    cursor.executemany(
        '''
        INSERT OR IGNORE INTO CourseRequirements (RequirementID, Department, Code, Grade, CourseID)
        VALUES (?, ?, ?, ?, ?)
        ''',
        [
            (1, 'CSC', 101, 2.0, 1),
            (2, 'CSC', 101, 2.0, 2),
            (3, 'MTH', 101, 2.0, 3),
            (4, 'CSC', 212, 2.0, 4),
            (5, 'CSC', 212, 2.0, 5),
            (6, 'CSC', 310, 2.0, 6),
            (7, 'CSC', 101, 2.0, 7),
            (8, 'CSC', 101, 2.0, 8),
            (9, 'MTH', 101, 2.0, 9),
            (10, 'CSC', 101, 2.0, 10),
            (11, 'CSC', 101, 2.0, 11),
            (12, 'MTH', 101, 2.0, 12),
            (13, 'CSC', 251, 2.0, 5),
            (14, 'CSC', 251, 2.0, 6),
            (15, 'CSC', 212, 2.0, 11),
            (16, 'CSC', 212, 2.0, 12),
        ]
    )

    cursor.executemany(
        '''
        INSERT OR IGNORE INTO Sections (SectionID, SectionNum, Instructor, MaxSeats, SeatsLeft, Modalim, Location, CourseID)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        [
            (1, 1, 'Dr. Smith', 35, 7, 'In Person', 'Science Hall 201', 1),
            (2, 1, 'Dr. Nguyen', 30, 10, 'In Person', 'Tech Building 115', 2),
            (3, 1, 'Dr. Patel', 40, 12, 'In Person', 'Math Center 302', 3),
            (4, 1, 'Dr. Carter', 32, 8, 'Hybrid', 'Science Hall 220', 4),
            (5, 1, 'Dr. Rivera', 28, 4, 'Online', 'Online', 5),
            (6, 1, 'Dr. Lopez', 30, 9, 'In Person', 'Engineering 101', 6),
            (7, 1, 'Dr. Smith', 35, 11, 'In Person', 'Science Hall 201', 7),
            (8, 1, 'Dr. Nguyen', 30, 6, 'In Person', 'Tech Building 115', 8),
            (9, 1, 'Dr. Patel', 40, 14, 'In Person', 'Math Center 302', 9),
            (10, 1, 'Dr. Smith', 35, 10, 'In Person', 'Science Hall 201', 10),
            (11, 1, 'Dr. Nguyen', 30, 8, 'In Person', 'Tech Building 115', 11),
            (12, 1, 'Dr. Patel', 40, 13, 'In Person', 'Math Center 302', 12),
        ]
    )

    cursor.executemany(
        '''
        INSERT OR IGNORE INTO MeetTimes (MeetTimeID, Day, StartTime, EndTime, SectionID)
        VALUES (?, ?, ?, ?, ?)
        ''',
        [
            (1, 'Monday', '09:00', '10:15', 1),
            (2, 'Wednesday', '09:00', '10:15', 1),
            (3, 'Tuesday', '11:00', '12:15', 2),
            (4, 'Thursday', '11:00', '12:15', 2),
            (5, 'Monday', '13:00', '14:15', 3),
            (6, 'Wednesday', '13:00', '14:15', 3),
            (7, 'Tuesday', '09:30', '10:45', 4),
            (8, 'Thursday', '09:30', '10:45', 4),
            (9, 'Monday', '18:00', '19:15', 5),
            (10, 'Wednesday', '18:00', '19:15', 5),
            (11, 'Tuesday', '14:00', '15:15', 6),
            (12, 'Thursday', '14:00', '15:15', 6),
            (13, 'Monday', '09:00', '10:15', 7),
            (14, 'Wednesday', '09:00', '10:15', 7),
            (15, 'Tuesday', '11:00', '12:15', 8),
            (16, 'Thursday', '11:00', '12:15', 8),
            (17, 'Monday', '13:00', '14:15', 9),
            (18, 'Wednesday', '13:00', '14:15', 9),
            (19, 'Monday', '09:00', '10:15', 10),
            (20, 'Wednesday', '09:00', '10:15', 10),
            (21, 'Tuesday', '11:00', '12:15', 11),
            (22, 'Thursday', '11:00', '12:15', 11),
            (23, 'Monday', '13:00', '14:15', 12),
            (24, 'Wednesday', '13:00', '14:15', 12),
        ]
    )



    conn.commit()

    # Quick verification for FK-linked hierarchy
    table_names = ['Terms', 'CoursesOffered', 'CourseRequirements', 'Sections', 'MeetTimes']
    for table_name in table_names:
        cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
        row_count = cursor.fetchone()[0]
        print(f'{table_name}: {row_count}')

    cursor.execute('''
        SELECT COUNT(*)
        FROM CoursesOffered c
        JOIN Terms t ON c.TermID = t.TermID
    ''')
    print(f'Courses with valid term FK: {cursor.fetchone()[0]}')

    cursor.execute('''
        SELECT COUNT(*)
        FROM CourseRequirements r
        JOIN CoursesOffered c ON r.CourseID = c.CourseID
    ''')
    print(f'Requirements with valid course FK: {cursor.fetchone()[0]}')

    cursor.execute('''
        SELECT COUNT(*)
        FROM Sections s
        JOIN CoursesOffered c ON s.CourseID = c.CourseID
    ''')
    print(f'Sections with valid course FK: {cursor.fetchone()[0]}')

    cursor.execute('''
        SELECT COUNT(*)
        FROM MeetTimes m
        JOIN Sections s ON m.SectionID = s.SectionID
    ''')
    print(f'MeetTimes with valid section FK: {cursor.fetchone()[0]}')
    
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