import json
import sqlite3
import os

database = "Test.db"
conn = None

# Utility function to set up the database with the required tables and schema
def setup_database():
    try:
        # Connect to sqlite database
        conn = sqlite3.connect(database)
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
                Name TEXT NOT NULL
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
                Urgency INTEGER NOT NULL,
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
    
    except Exception as e:
        raise RuntimeError(
            f"Failed to set up database: {e}"
        ) from e
    
    finally:
        # Ensure the connection is closed
        if conn:
            conn.close()

# Utility function to fetch all results from a query
def fetch_all(cursor: sqlite3.Cursor, query: str, params: tuple = ()):
	cursor.execute(query, params)
	return cursor.fetchall()

# Utility function to view the database hierarchy and contents in a readable format
def view_database_hierarchy():
    try:
        # Connect to sqlite database
        conn = sqlite3.connect(database)
        conn.execute('PRAGMA foreign_keys = ON')
        conn.row_factory = sqlite3.Row

        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()
        
        terms = fetch_all(
			cursor,
			'''
			SELECT TermID, Year, Season, Num
			FROM Terms
			ORDER BY Year, Season, Num, TermID
			''',
		)
        
        print(f'Database: {database}')
        print('Hierarchy: Terms -> CoursesOffered -> (CourseRequirements, Sections -> MeetTimes)\n')
        
        for term in terms:
            summer_part = f' {term["Num"]}' if term['Season'] == 'Summer' and term['Num'] else ''
            print(f'Term {term["TermID"]}: {term["Season"]}{summer_part} {term["Year"]}')
            
            courses = fetch_all(
				cursor,
				'''
				SELECT CourseID, Department, Code, Description, Credits
				FROM CoursesOffered
				WHERE TermID = ?
				ORDER BY Department, Code, CourseID
				''',
				(term['TermID'],),
			)
            
            if not courses:
                print('  └─ (no courses)')
                continue
            
            for course in courses:
                print(
					f'  ├─ Course {course["CourseID"]}: '
					f'{course["Department"]} {course["Code"]} '
					f'({course["Credits"]} cr) - {course["Description"]}'
				)
                
                requirements = fetch_all(
					cursor,
					'''
					SELECT RequirementID, Department, Code, Grade
					FROM CourseRequirements
					WHERE CourseID = ?
					ORDER BY RequirementID
					''',
					(course['CourseID'],),
				)
                
                if requirements:
                    for req in requirements:
                        req_code = req['Code'] if req['Code'] is not None else 'N/A'
                        req_grade = req['Grade'] if req['Grade'] is not None else 'N/A'
                        print(
							f'  │  ├─ Requirement {req["RequirementID"]}: '
							f'{req["Department"]} {req_code} min grade {req_grade}'
						)
                else:
                    print('  │  ├─ (no requirements)')
                
                sections = fetch_all(
					cursor,
					'''
					SELECT SectionID, SectionNum, Instructor, MaxSeats, SeatsLeft, Modalim, Location
					FROM Sections
					WHERE CourseID = ?
					ORDER BY SectionNum, SectionID
					''',
					(course['CourseID'],),
				)
                
                if not sections:
                    print('  │  └─ (no sections)')
                    continue
                
                for section in sections:
                    location = section['Location'] if section['Location'] else 'TBD'
                    print(
						f'  │  └─ Section {section["SectionID"]} '
						f'(#{section["SectionNum"]}): '
						f'{section["Instructor"]}, {section["Modalim"]}, {location}, '
						f'{section["SeatsLeft"]}/{section["MaxSeats"]} seats left'
					)
                    
                    meet_times = fetch_all(
						cursor,
						'''
						SELECT MeetTimeID, Day, StartTime, EndTime
						FROM MeetTimes
						WHERE SectionID = ?
						ORDER BY MeetTimeID
						''',
						(section['SectionID'],),
					)
                    
                    if meet_times:
                        for meet in meet_times:
                            print(
								f'  │     └─ MeetTime {meet["MeetTimeID"]}: '
								f'{meet["Day"]} {meet["StartTime"]}-{meet["EndTime"]}'
						    )
                    else:
                        print('  │     └─ (no meet times)')
                
            print()
    
    except Exception as e:
        raise RuntimeError(
            f"Failed to view database hierarchy: {e}"
        ) from e
    
    finally:
        # Ensure the connection is closed
        if conn:
            conn.close()

# Utility function to add a new term and its courses/sections from a JSON file
def add_new_term(json_file: str):
    try:
        # Connect to sqlite database
        conn = sqlite3.connect(database)
        conn.execute('PRAGMA foreign_keys = ON')

        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        # Load term data from JSON file
        with open(json_file, 'r') as f:
            term_data = json.load(f)

        # TODO: make the rest of this once json has added term info

        # Commit the changes to the database
        conn.commit()

    except Exception as e:
        raise RuntimeError(
            f"Failed to add new term to database: {e}"
        ) from e
    
    finally:
        # Ensure the connection is closed
        if conn:
            conn.close()

# Utility function to insert basic test data into the database for development/testing purposes
def insert_basic_test_data():
    try:
        # Connect to sqlite database
        conn = sqlite3.connect('Test.db')

        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        # Insert dummy test data
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

        # Commit the changes to the database
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
            f"Failed to insert test data into database: {e}"
        ) from e
    
    except Exception as e:
        raise RuntimeError(
            f"Unexpected error while initializing database: {e}"
        ) from e
    
    finally:
        # Ensure the connection is closed
        if conn:
            conn.close()