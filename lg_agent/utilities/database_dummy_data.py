# import dependencies
import sqlite3

conn = None

try:
    # Connect to sqlite database
    conn = sqlite3.connect('Test.db')
    conn.execute('PRAGMA foreign_keys = ON')

    # Create a cursor object to execute SQL commands
    cursor = conn.cursor()

    # Insert dummy test data in FK-safe order (parents before children)
    cursor.executemany(
        '''
        INSERT OR IGNORE INTO Terms (ID, StartDate, EndDate, Year, Season, Number)
        VALUES (?, ?, ?, ?, ?, ?)
        ''',
        [
            (1, '2026-01-12', '2026-05-08', 2026, 'Spring', None),
            (2, '2026-08-24', '2026-12-11', 2026, 'Fall', None),
            (3, '2026-05-18', '2026-06-26', 2026, 'Summer', 1),
            (4, '2026-06-29', '2026-08-07', 2026, 'Summer', 2),
        ],
    )

    cursor.executemany(
        '''
        INSERT OR IGNORE INTO Users (ID, Username, Password, AccountType)
        VALUES (?, ?, ?, ?)
        ''',
        [
            (1, 'alex_student', 'pass1234', 'Student'),
            (2, 'bri_student', 'pass1234', 'Student'),
            (3, 'casey_student', 'pass1234', 'Student'),
            (4, 'emily_advisor', 'pass1234', 'Advisor'),
            (5, 'james_advisor', 'pass1234', 'Advisor'),
        ],
    )

    cursor.executemany(
        '''
        INSERT OR IGNORE INTO Advisors (ID, Name, UserID)
        VALUES (?, ?, ?)
        ''',
        [
            (1, 'Dr. Emily Carter', 4),
            (2, 'Prof. James Nguyen', 5),
        ],
    )

    cursor.executemany(
        '''
        INSERT OR IGNORE INTO Students (
            ID,
            Name,
            GPA,
            CreditsEarned,
            IntendedGraduationTerm,
            AdvisorID,
            UserID
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        [
            (1, 'Alex Johnson', 3.42, 45, 'Spring 2028', 1, 1),
            (2, 'Brianna Lee', 3.78, 78, 'Fall 2027', 2, 2),
            (3, 'Casey Patel', 3.15, 30, 'Spring 2029', 1, 3),
        ],
    )

    cursor.executemany(
        '''
        INSERT OR IGNORE INTO MajorsAndMinors (ID, Title, Type, StudentID)
        VALUES (?, ?, ?, ?)
        ''',
        [
            (1, 'Computer Science', 'Major', 1),
            (2, 'Mathematics', 'Minor', 1),
            (3, 'Computer Science', 'Major', 2),
            (4, 'Data Science', 'Minor', 2),
            (5, 'Computer Science', 'Major', 3),
        ],
    )

    cursor.executemany(
        '''
        INSERT OR IGNORE INTO Interests (ID, Interest, StudentID)
        VALUES (?, ?, ?)
        ''',
        [
            (1, 'Artificial Intelligence', 1),
            (2, 'Cybersecurity', 1),
            (3, 'Software Engineering', 2),
            (4, 'Human-Computer Interaction', 2),
            (5, 'Data Analytics', 3),
        ],
    )

    cursor.executemany(
        '''
        INSERT OR IGNORE INTO Events (
            ID,
            Name,
            Description,
            StartDate,
            EndDate,
            StartTime,
            EndTime,
            Location
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        [
            (1, 'Resume Workshop', 'Career services resume review session.', '2026-03-20', '2026-03-20', '15:00', '16:30', 'Career Center 101'),
            (2, 'AI Research Talk', 'Guest lecture on practical LLM systems.', '2026-03-28', '2026-03-28', '13:00', '14:30', 'Science Hall 220'),
            (3, 'Internship Fair', 'Regional tech internship networking event.', '2026-04-05', '2026-04-05', '10:00', '14:00', 'Student Union Ballroom'),
        ],
    )

    cursor.executemany(
        '''
        INSERT OR IGNORE INTO CoursesOffered (ID, Department, Code, Description, Credits, TermID)
        VALUES (?, ?, ?, ?, ?, ?)
        ''',
        [
            (1, 'CSC', 212, 'Data Structures and Algorithms', 3, 1),
            (2, 'CSC', 251, 'Computer Organization and Architecture', 3, 1),
            (3, 'MTH', 231, 'Discrete Mathematics', 3, 1),
            (4, 'CSC', 310, 'Database Systems', 3, 2),
            (5, 'CSC', 340, 'Artificial Intelligence', 3, 2),
            (6, 'CSC', 450, 'Software Engineering', 3, 2),
            (7, 'CSC', 212, 'Data Structures and Algorithms', 3, 3),
            (8, 'CSC', 251, 'Computer Organization and Architecture', 3, 3),
            (9, 'MTH', 231, 'Discrete Mathematics', 3, 3),
            (10, 'CSC', 212, 'Data Structures and Algorithms', 3, 4),
            (11, 'CSC', 251, 'Computer Organization and Architecture', 3, 4),
            (12, 'MTH', 231, 'Discrete Mathematics', 3, 4),
        ],
    )

    cursor.executemany(
        '''
        INSERT OR IGNORE INTO CourseRequirements (ID, RequiredCourseID, RequiredGrade, CourseID)
        VALUES (?, ?, ?, ?)
        ''',
        [
            (1, 101, 2.0, 1),
            (2, 101, 2.0, 2),
            (3, 101, 2.0, 3),
            (4, 1, 2.0, 4),
            (5, 1, 2.0, 5),
            (6, 4, 2.0, 6),
            (7, 101, 2.0, 7),
            (8, 101, 2.0, 8),
            (9, 101, 2.0, 9),
            (10, 101, 2.0, 10),
            (11, 101, 2.0, 11),
            (12, 101, 2.0, 12),
            (13, 2, 2.0, 5),
            (14, 2, 2.0, 6),
            (15, 1, 2.0, 11),
            (16, 1, 2.0, 12),
        ],
    )

    cursor.executemany(
        '''
        INSERT OR IGNORE INTO Sections (ID, SectionNum, Instructor, MaxSeats, SeatsLeft, Modality, Location, CourseID)
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
        ],
    )

    cursor.executemany(
        '''
        INSERT OR IGNORE INTO MeetTimes (ID, Day, StartTime, EndTime, SectionID)
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
        ],
    )

    # Commit the changes to the database
    conn.commit()

    # Quick verification for FK-linked hierarchy
    table_names = [
        'Terms',
        'Users',
        'Advisors',
        'Students',
        'MajorsAndMinors',
        'Interests',
        'Events',
        'RelevantEvents',
        'ChatLogs',
        'CoursesOffered',
        'CourseRequirements',
        'Sections',
        'MeetTimes',
    ]
    for table_name in table_names:
        cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
        row_count = cursor.fetchone()[0]
        print(f'{table_name}: {row_count}')

    cursor.execute('''
        SELECT COUNT(*)
        FROM CoursesOffered c
        JOIN Terms t ON c.TermID = t.ID
    ''')
    print(f'Courses with valid term FK: {cursor.fetchone()[0]}')

    cursor.execute('''
        SELECT COUNT(*)
        FROM CourseRequirements r
        JOIN CoursesOffered c ON r.CourseID = c.ID
    ''')
    print(f'Requirements with valid course FK: {cursor.fetchone()[0]}')

    cursor.execute('''
        SELECT COUNT(*)
        FROM Sections s
        JOIN CoursesOffered c ON s.CourseID = c.ID
    ''')
    print(f'Sections with valid course FK: {cursor.fetchone()[0]}')

    cursor.execute('''
        SELECT COUNT(*)
        FROM MeetTimes m
        JOIN Sections s ON m.SectionID = s.ID
    ''')
    print(f'MeetTimes with valid section FK: {cursor.fetchone()[0]}')

    cursor.execute('''
        SELECT COUNT(*)
        FROM Students st
        JOIN Users u ON st.UserID = u.ID
    ''')
    print(f'Students with valid user FK: {cursor.fetchone()[0]}')

    cursor.execute('''
        SELECT COUNT(*)
        FROM Students st
        LEFT JOIN Advisors a ON st.AdvisorID = a.ID
        WHERE st.AdvisorID IS NULL OR a.ID IS NOT NULL
    ''')
    print(f'Students with valid advisor FK/NULL: {cursor.fetchone()[0]}')

    cursor.execute('''
        SELECT COUNT(*)
        FROM Advisors a
        JOIN Users u ON a.UserID = u.ID
    ''')
    print(f'Advisors with valid user FK: {cursor.fetchone()[0]}')

    cursor.execute('''
        SELECT COUNT(*)
        FROM MajorsAndMinors mm
        JOIN Students st ON mm.StudentID = st.ID
    ''')
    print(f'Majors/Minors with valid student FK: {cursor.fetchone()[0]}')

    cursor.execute('''
        SELECT COUNT(*)
        FROM Interests i
        JOIN Students st ON i.StudentID = st.ID
    ''')
    print(f'Interests with valid student FK: {cursor.fetchone()[0]}')

    cursor.execute('''
        SELECT COUNT(*)
        FROM ChatLogs cl
        JOIN Students st ON cl.StudentID = st.ID
    ''')
    print(f'Chat logs with valid student FK: {cursor.fetchone()[0]}')

    cursor.execute('''
        SELECT COUNT(*)
        FROM RelevantEvents re
        JOIN Students st ON re.StudentID = st.ID
        JOIN Events e ON re.EventID = e.ID
    ''')
    print(f'Relevant events with valid event/student FK: {cursor.fetchone()[0]}')
    
except Exception as exc:
    raise RuntimeError("Failed to insert dummy data into the database.") from exc
finally:
    # Ensure the connection is closed
    if conn:
        conn.close()