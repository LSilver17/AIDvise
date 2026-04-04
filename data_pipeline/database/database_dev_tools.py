import json
import re
import re
import sqlite3
import os

database = "AdvisorDB.db"
conn = None

# Utility function to set up the database with the required tables and schema
def setup_database():
    try:
        # Connect to sqlite database
        conn = sqlite3.connect(database)
        conn.execute('PRAGMA foreign_keys = ON')

        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        # Table with all courses offered by the college
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS Courses(
                ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                Department TEXT NOT NULL,
                Code INTEGER NOT NULL,
                Name TEXT NOT NULL UNIQUE,
                Description TEXT NOT NULL,
                Credits INTEGER NOT NULL,
                Requirements TEXT
            )'''
        )

        # Create tables for all majors/minors offered at the college
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS MajorsAndMinors(
                ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                Title TEXT NOT NULL,
                Description TEXT NOT NULL,
                CreditsRequired INTEGER NOT NULL,
                Type TEXT NOT NULL CHECK(Type IN ('Major', 'Minor'))
            )'''
        )
        # Table for required courses for each major/minor, linked to the major/minor via ParentID foreign key
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS MajorMinorRequiredCourses(
                ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                ParentID INTEGER NOT NULL,
                FOREIGN KEY (ParentID) REFERENCES MajorsAndMinors(ID)
                    ON DELETE CASCADE
            )'''
        )
        # Table for options for required courses for each major/minor, linked to the requirement via ParentID foreign key and to the course via CourseID foreign key
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS MajorMinorRequiredCourseOptions(
                ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                CourseID INTEGER NOT NULL,
                ParentID INTEGER NOT NULL,
                FOREIGN KEY (CourseID) REFERENCES Courses(ID)
                    ON DELETE CASCADE,
                FOREIGN KEY (ParentID) REFERENCES MajorMinorRequiredCourses(ID)
                    ON DELETE CASCADE
            )'''
        )

        # Table for upcoming terms (semesters) offered at the college
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS Terms(
                ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                Year INTEGER NOT NULL,
                Season TEXT NOT NULL,
                Number INTEGER
            )'''
        )
        # Table for courses offered in each term, linked to the term via ParentID foreign key and to the course via CourseID foreign key
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS CoursesOffered(
                ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                CourseID INTEGER NOT NULL,
                ParentID INTEGER NOT NULL,
                FOREIGN KEY (CourseID) REFERENCES Courses(ID)
                    ON DELETE CASCADE,
                FOREIGN KEY (ParentID) REFERENCES Terms(ID)
                    ON DELETE CASCADE
            )'''
        )
        # Table for specific sections of each course offered in a term, linked to the course offering via ParentID foreign key
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS Sections(
                ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                SectionNum INTEGER NOT NULL,
                Instructor TEXT NOT NULL,
                StartDate DATE NOT NULL,
                EndDate DATE NOT NULL,
                Status TEXT NOT NULL CHECK(Status IN ('Open', 'Closed', 'Reopened')),
                MaxSeats INTEGER NOT NULL,
                SeatsLeft INTEGER NOT NULL,
                Method TEXT NOT NULL,
                Location TEXT,
                ParentID INTEGER NOT NULL,
                FOREIGN KEY (ParentID) REFERENCES CoursesOffered(ID)
                    ON DELETE CASCADE
            )'''
        )
        # Table for meeting times for each section, linked to the section via ParentID foreign key
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS MeetTimes(
                ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                Day TEXT NOT NULL,
                StartTime TIME NOT NULL,
                EndTime TIME NOT NULL,
                ParentID INTEGER NOT NULL,
                FOREIGN KEY (ParentID) REFERENCES Sections(ID)
                    ON DELETE CASCADE
            )'''
        )

        # Table for users of the advising system (students and advisors), with a field to distinguish between the two types of users and a unique constraint on the username
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS Users(
                ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                Username TEXT NOT NULL UNIQUE,
                Password TEXT NOT NULL,
                AccountType TEXT NOT NULL CHECK(AccountType IN ('Student', 'Advisor'))
            )'''
        )

        # Table for upcoming events related to the college
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS Events(
                ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                Name TEXT NOT NULL,
                Description TEXT NOT NULL
            )'''
        )
        # Table for specific dates/times for each event, linked to the event via ParentID foreign key
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS EventDates(
                ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                Date DATE NOT NULL,
                StartTime TIME NOT NULL,
                EndTime TIME NOT NULL,
                Location TEXT,
                ParentID INTEGER NOT NULL,
                FOREIGN KEY (ParentID) REFERENCES Events(ID)
                    ON DELETE CASCADE
            )'''
        )

        # Table for advisors, linked to the Users table via ParentID foreign key with a unique constraint to ensure a 1-1 relationship between users and advisors
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS Advisors(
                ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                Name TEXT,
                ParentID INTEGER NOT NULL UNIQUE,
                FOREIGN KEY (ParentID) REFERENCES Users(ID)
                    ON DELETE CASCADE
            )'''
        )

        # Table for students, linked to the Users table via ParentID foreign key with a unique constraint to ensure a 1-1 relationship between users and students, and linked to advisors via AdvisorID foreign key with a SET NULL on delete to allow students to remain in the system without an advisor if their advisor is deleted
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS Students(
                ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                Name TEXT,
                GPA REAL,
                CreditsEarned INTEGER,
                IntendedGraduationTerm TEXT,
                AdvisorID INTEGER,
                ParentID INTEGER NOT NULL UNIQUE,
                FOREIGN KEY (AdvisorID) REFERENCES Advisors(ID)
                    ON DELETE SET NULL,
                FOREIGN KEY (ParentID) REFERENCES Users(ID)
                    ON DELETE CASCADE
            )'''
        )
        # Table for majors and minors for each student, linked to the student via ParentID foreign key and to the MajorsAndMinors table via MajorMinorID foreign key
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS MajorsAndMinors(
                ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                MajorMinorID INTEGER NOT NULL,
                ParentID INTEGER NOT NULL,
                FOREIGN KEY (MajorMinorID) REFERENCES MajorsAndMinors(ID)
                    ON DELETE CASCADE,
                FOREIGN KEY (ParentID) REFERENCES Students(ID)
                    ON DELETE CASCADE
            )'''
        )
        # Table for courses taken by each student, linked to the student via ParentID foreign key and to the Courses table via CourseID foreign key
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS CoursesTaken(
                ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                CourseID INTEGER NOT NULL,
                ParentID INTEGER NOT NULL,
                FOREIGN KEY (CourseID) REFERENCES Courses(ID)
                    ON DELETE CASCADE,
                FOREIGN KEY (ParentID) REFERENCES Students(ID)
                    ON DELETE CASCADE
            )'''
        )
        # Table for interests for each student, linked to the student via ParentID foreign key
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS Interests(
                ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                Interest TEXT NOT NULL,
                ParentID INTEGER NOT NULL,
                FOREIGN KEY (ParentID) REFERENCES Students(ID)
                    ON DELETE CASCADE
            )'''
        )
        # Table for chat logs between each student and the chatbot, linked to the student via ParentID foreign key
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS ChatLogs(
                ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                Log TEXT NOT NULL,
                Timestamp DATETIME NOT NULL,
                ParentID INTEGER NOT NULL,
                FOREIGN KEY (ParentID) REFERENCES Students(ID)
                    ON DELETE CASCADE
            )'''
        )
        # Table for relevant events for each student, linked to the student via ParentID foreign key and to the Events table via EventID foreign key
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS RelevantEvents(
                ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                Urgency INTEGER NOT NULL,
                EventID INTEGER NOT NULL,
                ParentID INTEGER NOT NULL,
                FOREIGN KEY (ParentID) REFERENCES Students(ID)
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

# Utility function to populate the course catalog in the database from a JSON file containing course information
def populate_course_catalog(json_file: str):
    # TODO: implement this function once we have a JSON file with course info to work with
    pass
    try:
        # Connect to sqlite database
        conn = sqlite3.connect(database)

        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        # Drop course catalog tables
        cursor.execute('DROP TABLE IF EXISTS Courses')
        cursor.execute('DROP TABLE IF EXISTS CourseRequiredCourses')
        cursor.execute('DROP TABLE IF EXISTS CourseRequiredCourseOptions')
        cursor.execute('DROP TABLE IF EXISTS MiscCourseRequirements')

        # Commit the changes to the database
        conn.commit()
    
    except Exception as e:
        raise RuntimeError(
            f"Failed to reset course catalog in database: {e}"
        ) from e
    
    finally:
        # Ensure the connection is closed
        if conn:
            conn.close()

# Utility function to populate the majors and minors catalog in the database from a JSON file containing major/minor information
def populate_majors_and_minors_catalog(json_file: str):
    # TODO: implement this function once we have a JSON file with major/minor info to work with
    pass

# Utility function to reset the course catalog tables
def reset_course_catalog():
    try:
        # Connect to sqlite database
        conn = sqlite3.connect(database)

        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        # Drop course catalog tables
        cursor.execute('DROP TABLE IF EXISTS Courses')
        cursor.execute('DROP TABLE IF EXISTS CourseRequiredCourses')
        cursor.execute('DROP TABLE IF EXISTS CourseRequiredCourseOptions')
        cursor.execute('DROP TABLE IF EXISTS MiscCourseRequirements')

        # Commit the changes to the database
        conn.commit()
    
    except Exception as e:
        raise RuntimeError(
            f"Failed to reset course catalog in database: {e}"
        ) from e
    
    finally:
        # Ensure the connection is closed
        if conn:
            conn.close()

# Utility function to reset the majors and minors catalog tables
def reset_majors_and_minors_catalog():
    try:
        # Connect to sqlite database
        conn = sqlite3.connect(database)

        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        # Drop majors and minors catalog tables
        cursor.execute('DROP TABLE IF EXISTS MajorsAndMinors')
        cursor.execute('DROP TABLE IF EXISTS MajorMinorRequiredCourses')
        cursor.execute('DROP TABLE IF EXISTS MajorMinorRequiredCourseOptions')

        # Commit the changes to the database
        conn.commit()
    
    except Exception as e:
        raise RuntimeError(
            f"Failed to reset majors and minors catalog in database: {e}"
        ) from e
    
    finally:
        # Ensure the connection is closed
        if conn:
            conn.close()

# Utility function to reset the terms and courses offered tables
def reset_terms_and_courses():
    try:
        # Connect to sqlite database
        conn = sqlite3.connect(database)

        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        # Drop terms and courses offered tables
        cursor.execute('DROP TABLE IF EXISTS Terms')
        cursor.execute('DROP TABLE IF EXISTS CoursesOffered')
        cursor.execute('DROP TABLE IF EXISTS Sections')
        cursor.execute('DROP TABLE IF EXISTS MeetTimes')

        # Commit the changes to the database
        conn.commit()
    
    except Exception as e:
        raise RuntimeError(
            f"Failed to reset terms and courses in database: {e}"
        ) from e
    
    finally:
        # Ensure the connection is closed
        if conn:
            conn.close()

# Utility function to reset the events tables
def reset_events():
    try:
        # Connect to sqlite database
        conn = sqlite3.connect(database)

        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        # Drop events tables
        cursor.execute('DROP TABLE IF EXISTS Events')
        cursor.execute('DROP TABLE IF EXISTS EventDates')

        # Commit the changes to the database
        conn.commit()
    
    except Exception as e:
        raise RuntimeError(
            f"Failed to reset events in database: {e}"
        ) from e
    
    finally:
        # Ensure the connection is closed
        if conn:
            conn.close()

# Utility function to reset the users, advisors, and students tables
def reset_users():
    try:
        # Connect to sqlite database
        conn = sqlite3.connect(database)

        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        # Drop users, advisors, and students tables
        cursor.execute('DROP TABLE IF EXISTS Users')
        cursor.execute('DROP TABLE IF EXISTS Advisors')
        cursor.execute('DROP TABLE IF EXISTS Students')
        cursor.execute('DROP TABLE IF EXISTS MajorsAndMinors')
        cursor.execute('DROP TABLE IF EXISTS CoursesTaken')
        cursor.execute('DROP TABLE IF EXISTS Interests')
        cursor.execute('DROP TABLE IF EXISTS ChatLogs')
        cursor.execute('DROP TABLE IF EXISTS RelevantEvents')

        # Commit the changes to the database
        conn.commit()
    
    except Exception as e:
        raise RuntimeError(
            f"Failed to reset users in database: {e}"
        ) from e
    
    finally:
        # Ensure the connection is closed
        if conn:
            conn.close()

# Utility function to reset all tables in the database except for course catalog tables
def reset_all():
    reset_course_catalog()
    reset_majors_and_minors_catalog()
    reset_terms_and_courses()
    reset_events()
    reset_users()

    try:
        # Connect to sqlite database
        conn = sqlite3.connect(database)
        conn.execute('PRAGMA foreign_keys = ON')
        conn.row_factory = sqlite3.Row

        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()
        
        # ── Advisors -> Students -> (MajorsAndMinors, Interests, ChatLogs, RelevantEvents -> Events) ──
        print(f'Database: {database}')
        print('\n══ ADVISORS ══')
        print('Hierarchy: Users(Advisor) -> Advisors -> Students -> (MajorsAndMinors, Interests, ChatLogs, RelevantEvents -> Events)\n')
        
        advisors = cursor.execute(
			'''
			SELECT a.ID, a.Name, a.ParentID, u.Username
			FROM Advisors a
			JOIN Users u ON a.ParentID = u.ID
			ORDER BY a.ID
			''',
		).fetchall()
        
        for advisor in advisors:
            print(f'Advisor {advisor["ID"]}: {advisor["Name"]} (user: {advisor["Username"]})')
            
            students = cursor.execute(
				'''
				SELECT s.ID, s.Name, s.GPA, s.CreditsEarned, s.IntendedGraduationTerm, u.Username
				FROM Students s
				JOIN Users u ON s.ParentID = u.ID
				WHERE s.AdvisorID = ?
				ORDER BY s.ID
				''',
				(advisor['ID'],),
			).fetchall()
            
            if not students:
                print('  └─ (no students)')
                continue
            
            for student in students:
                gpa = student['GPA'] if student['GPA'] is not None else 'N/A'
                credits_earned = student['CreditsEarned'] if student['CreditsEarned'] is not None else 'N/A'
                grad_term = student['IntendedGraduationTerm'] if student['IntendedGraduationTerm'] else 'N/A'
                print(
					f'  ├─ Student {student["ID"]}: {student["Name"]} '
					f'(user: {student["Username"]}, GPA: {gpa}, '
					f'Credits: {credits_earned}, Grad: {grad_term})'
				)
                
                majors_minors = cursor.execute(
					'''
					SELECT ID, Title, Type
					FROM MajorsAndMinors
					WHERE ParentID = ?
					ORDER BY Type, Title
					''',
					(student['ID'],),
				).fetchall()

                if majors_minors:
                    for mm in majors_minors:
                        print(f'  │  ├─ {mm["Type"]}: {mm["Title"]}')
                else:
                    print('  │  ├─ (no majors/minors)')
                    
                interests = cursor.execute(
					'''
					SELECT ID, Interest
					FROM Interests
					WHERE ParentID = ?
					ORDER BY ID
					''',
					(student['ID'],),
				).fetchall()
                
                if interests:
                    interest_list = ', '.join(i['Interest'] for i in interests)
                    print(f'  │  ├─ Interests: {interest_list}')
                else:
                    print('  │  ├─ Interests: (none)')
                
                chat_logs = cursor.execute(
					'''
					SELECT ID, Log, Timestamp
					FROM ChatLogs
					WHERE ParentID = ?
					ORDER BY Timestamp
					''',
					(student['ID'],),
				).fetchall()
                
                if chat_logs:
                    for log in chat_logs:
                        print(f'  │  ├─ ChatLog {log["ID"]} [{log["Timestamp"]}]: {log["Log"]}')
                else:
                    print('  │  ├─ (no chat logs)')
                    
                relevant_events = cursor.execute(
					'''
					SELECT re.ID, re.Urgency, e.Name, e.StartDate, e.StartTime, e.Location
					FROM RelevantEvents re
					JOIN Events e ON re.EventID = e.ID
					WHERE re.ParentID = ?
					ORDER BY re.Urgency, e.StartDate
					''',
					(student['ID'],),
				).fetchall()
                
                if relevant_events:
                    for re_row in relevant_events:
                        loc = re_row['Location'] if re_row['Location'] else 'TBD'
                        print(
							f'  │  └─ Event {re_row["ID"]} [{re_row["Urgency"]}]: '
							f'{re_row["Name"]} on {re_row["StartDate"]} at {re_row["StartTime"]}, {loc}'
						)
                else:
                    print('  │  └─ (no relevant events)')
            
            print()


    finally:
        # Ensure the connection is closed
        if conn:
            conn.close()

# Utility function to add a new term and its courses/sections from a JSON file
# TODO: update this to follow new database structure
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

        # TODO: Once term info is added to the JSON, make code to add the new term to the Terms table and get its ID to use as the ParentID for the courses.

        # Add the courses for the new term to the CoursesOffered table, linking them to the term via ParentID
        for course in term_data['Courses']:
            #check if course already exists for the term to avoid duplicates
            existing_course = cursor.execute(
                '''
                SELECT ID
                FROM CoursesOffered
                WHERE Department = ? AND Code = ? AND ParentID = ?
                ''',
                (course['Department'], course['Code'], course['ParentID'])
            ).fetchone()

            # if the course doesn't already exist for the term, insert it into the CoursesOffered table with the appropriate ParentID linking it to the term
            if not existing_course:
                cursor.execute(
                    '''
                    INSERT INTO CoursesOffered (Department, Code, Name, Description, Credits, ParentID)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''',
                    (
                        course['department'],
                        int(course['course_number']),
                        course['name'],
                        "lorem ipsum",  # TODO: change this placeholder description once we add descriptions to the JSON
                        float(course['credits']),
                        1 # TODO: change this placeholder ParentID to link to the correct term based on the JSON data once we add term info to the JSON
                    )
                )

                # TODO: Once requirements are added to the JSON, make code to add them to the CourseRequirements table for each course, linking them to the course via ParentID
            
            # add the specific section of the course to the Sections table, linking it to the course via ParentID
            cursor.execute(
                '''
                INSERT INTO Sections (SectionNum, Instructor, StartDate, EndDate, MaxSeats, SeatsLeft, Method, Location, ParentID)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    int(course['section']),
                    course['instructor'],
                    int(course['begin_date']),
                    int(course['end_date']),
                    course['status'],
                    int(course['seats_total']),
                    int(course['seats_open']),
                    course['method'],
                    course['location'],
                    (existing_course['ID'] if existing_course else cursor.lastrowid)
                )
            )

            section_id = cursor.lastrowid
            
            # seperate days from times since the JSON format has them combined and we need to split them to fit our schema
            day_initials, time_unsplit = course['days_time'].split()
            start_time = time_unsplit[:5]
            if time_unsplit[5] == '-':
                end_time = time_unsplit[6:]
            else:
                start_time_am_pm = time_unsplit[5:7]
                end_time = time_unsplit[7:]
                end_time_am_pm = time_unsplit[7:9]

            # convert start and end times to 24 hour format based on the AM/PM indicators
            if start_time_am_pm:
                if start_time == '12:00':
                    start_time = '00:00'
                else:
                    start_time = f'{int(start_time[:2]) + 12}:{start_time[3:]}'

            if end_time_am_pm == 'PM':
                if end_time == '12:00':
                    end_time = '00:00'
                else:
                    end_time = f'{int(end_time[:2]) + 12}:{end_time[3:]}'

            # Seperate each day initiall from the string of day initials
            day_list = list(day_initials)

            # Convert day initials to full day names
            day_mapping = {
                'M': 'Monday',
                'T': 'Tuesday',
                'W': 'Wednesday',
                'R': 'Thursday',
                'F': 'Friday'
            }

            for day_initials, i in day_list:
                day_list[i] = day_mapping[day_initials]

            # for each day, insert a meet time entry into the MeetTimes table linked to the section via ParentID
            for day in day_list:
                cursor.execute(
                    '''
                    INSERT INTO MeetTimes (Day, StartTime, EndTime, ParentID)
                    VALUES (?, ?, ?, ?)
                    ''',
                    (day, start_time, end_time, section_id)
                )

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

    try:
        # Connect to sqlite database
        conn = sqlite3.connect(database)

        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        # Insert dummy test data for course hierarchy
        cursor.executemany(
            '''
            INSERT OR IGNORE INTO Terms (Year, Season, Number)
            VALUES (?, ?, ?)
            ''',
            [
                (2026, 'Spring', None),
                (2026, 'Fall', None),
                (2026, 'Summer', 1),
                (2026, 'Summer', 2),
            ],
        )

        cursor.executemany(
            '''
            INSERT OR IGNORE INTO CoursesOffered (Department, Code, Name, Description, Credits, ParentID)
            VALUES (?, ?, ?, ?, ?, ?)
            ''',
            [
                ('CSC', 212, 'Data Structures and Algorithms', 'A study of data structures and algorithms for problem-solving', 3, 1),
                ('CSC', 251, 'Computer Organization and Architecture', 'An introduction to computer organization and architecture', 3, 1),
                ('MTH', 231, 'Discrete Mathematics', 'A study of discrete mathematical structures and their applications', 3, 1)
            ],
        )

        cursor.executemany(
            '''
            INSERT OR IGNORE INTO CoursesOffered (Department, Code, Name, Description, Credits, ParentID)
            VALUES (?, ?, ?, ?, ?, ?)
            ''',
            [
                ('CSC', 310, 'Database Systems', 'A study of database systems and their applications', 3, 2),
                ('CSC', 340, 'Artificial Intelligence', 'An introduction to artificial intelligence and its applications', 3, 2),
                ('CSC', 450, 'Software Engineering', 'A study of software engineering principles and practices', 3, 2)
            ],
        )

        cursor.executemany(
            '''
            INSERT OR IGNORE INTO CoursesOffered (Department, Code, Name, Description, Credits, ParentID)
            VALUES (?, ?, ?, ?, ?, ?)
            ''',
            [
                ('CSC', 212, 'Data Structures and Algorithms', 'A study of data structures and algorithms for problem-solving', 3, 3),
                ('CSC', 251, 'Computer Organization and Architecture', 'An introduction to computer organization and architecture', 3, 3),
                ('MTH', 231, 'Discrete Mathematics', 'A study of discrete mathematical structures and their applications', 3, 3)
            ],
        )

        cursor.executemany(
            '''
            INSERT OR IGNORE INTO CoursesOffered (Department, Code, Name, Description, Credits, ParentID)
            VALUES (?, ?, ?, ?, ?, ?)
            ''',
            [
                ('CSC', 212, 'Data Structures and Algorithms', 'A study of data structures and algorithms for problem-solving', 3, 4),
                ('CSC', 251, 'Computer Organization and Architecture', 'An introduction to computer organization and architecture', 3, 4),
                ('MTH', 231, 'Discrete Mathematics', 'A study of discrete mathematical structures and their applications', 3, 4)
            ],
        )

        cursor.executemany(
            '''
            INSERT OR IGNORE INTO CourseRequirements (Department, Code, Grade, ParentID)
            VALUES (?, ?, ?, ?)
            ''',
            [
                ('CSC', 101, 2.0, 1),
                ('CSC', 101, 2.0, 2),
                ('MTH', 101, 2.0, 3),
                ('CSC', 212, 2.0, 4),
                ('CSC', 212, 2.0, 5),
                ('CSC', 310, 2.0, 6),
                ('CSC', 101, 2.0, 7),
                ('CSC', 101, 2.0, 8),
                ('MTH', 101, 2.0, 9),
                ('CSC', 101, 2.0, 10),
                ('CSC', 101, 2.0, 11),
                ('MTH', 101, 2.0, 12),
                ('CSC', 251, 2.0, 5),
                ('CSC', 251, 2.0, 6),
                ('CSC', 212, 2.0, 11),
                ('CSC', 212, 2.0, 12),
            ]
        )

        cursor.executemany(
            '''
            INSERT OR IGNORE INTO Sections (SectionNum, Instructor, StartDate, EndDate, Status, MaxSeats, SeatsLeft, Method, Location, ParentID)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            [
                (1, 'Dr. Smith', 35, 7, 'Open', 30, 25, 'In Person', 'Science Hall 201', 1),
                (1, 'Dr. Nguyen', 30, 10, 'Open', 25, 20, 'In Person', 'Tech Building 115', 2),
                (1, 'Dr. Patel', 40, 12, 'Open', 25, 20, 'In Person', 'Math Center 302', 3),
                (1, 'Dr. Carter', 32, 8, 'Hybrid', 25, 20, 'Hybrid', 'Science Hall 220', 4),
                (1, 'Dr. Rivera', 28, 4, 'Online', 25, 20, 'Online', 'Online', 5),
                (1, 'Dr. Lopez', 30, 9, 'Open', 25, 20, 'In Person', 'Engineering 101', 6),
                (1, 'Dr. Smith', 35, 11, 'Open', 30, 25, 'In Person', 'Science Hall 201', 7),
                (1, 'Dr. Nguyen', 30, 6, 'Open', 25, 20, 'In Person', 'Tech Building 115', 8),
                (1, 'Dr. Patel', 40, 14, 'Open', 25, 20, 'In Person', 'Math Center 302', 9),
                (1, 'Dr. Carter', 32, 10, 'Hybrid', 25, 20, 'Hybrid', 'Science Hall 220', 10),
                (1, 'Dr. Rivera', 28, 5, 'Online', 25, 20, 'Online', 'Online', 11),
                (1, 'Dr. Lopez', 30, 13, 'Open', 25, 20, 'In Person', 'Engineering 101', 12),
            ]
        )

        cursor.executemany(
            '''
            INSERT OR IGNORE INTO MeetTimes (Day, StartTime, EndTime, ParentID)
            VALUES (?, ?, ?, ?)
            ''',
            [
                ('Monday', '09:00', '10:15', 1),
                ('Wednesday', '09:00', '10:15', 1),
                ('Tuesday', '11:00', '12:15', 2),
                ('Thursday', '11:00', '12:15', 2),
                ('Monday', '13:00', '14:15', 3),
                ('Wednesday', '13:00', '14:15', 3),
                ('Tuesday', '09:30', '10:45', 4),
                ('Thursday', '09:30', '10:45', 4),
                ('Monday', '18:00', '19:15', 5),
                ('Wednesday', '18:00', '19:15', 5),
                ('Tuesday', '14:00', '15:15', 6),
                ('Thursday', '14:00', '15:15', 6),
                ('Monday', '09:00', '10:15', 7),
                ('Wednesday', '09:00', '10:15', 7),
                ('Tuesday', '11:00', '12:15', 8),
                ('Thursday', '11:00', '12:15', 8),
                ('Monday', '13:00', '14:15', 9),
                ('Wednesday', '13:00', '14:15', 9),
                ('Monday', '09:00', '10:15', 10),
                ('Wednesday', '09:00', '10:15', 10),
                ('Tuesday', '11:00', '12:15', 11),
                ('Thursday', '11:00', '12:15', 11),
                ('Monday', '13:00', '14:15', 12),
                ('Wednesday', '13:00', '14:15', 12),
            ]
        )

        # Insert dummy test data for events
        cursor.executemany(
            '''
            INSERT OR IGNORE INTO Events (
                Name,
                Description,
                StartDate,
                EndDate,
                StartTime,
                EndTime,
                Location
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''',
            [
                ('Resume Workshop', 'Career services resume review session.', '2026-03-20', '2026-03-20', '15:00', '16:30', 'Career Center 101'),
                ('AI Research Talk', 'Guest lecture on practical LLM systems.', '2026-03-28', '2026-03-28', '13:00', '14:30', 'Science Hall 220'),
                ('Internship Fair', 'Regional tech internship networking event.', '2026-04-05', '2026-04-05', '10:00', '14:00', 'Student Union Ballroom'),
            ],
        )

        # Commit the changes to the database
        conn.commit()

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
            JOIN Terms t ON c.ParentID = t.ID
        ''')
        print(f'Courses with valid term FK: {cursor.fetchone()[0]}')

        cursor.execute('''
            SELECT COUNT(*)
            FROM CourseRequirements r
            JOIN CoursesOffered c ON r.ParentID = c.ID
        ''')
        print(f'Requirements with valid course FK: {cursor.fetchone()[0]}')

        cursor.execute('''
            SELECT COUNT(*)
            FROM Sections s
            JOIN CoursesOffered c ON s.ParentID = c.ID
        ''')
        print(f'Sections with valid course FK: {cursor.fetchone()[0]}')

        cursor.execute('''
            SELECT COUNT(*)
            FROM MeetTimes m
            JOIN Sections s ON m.ParentID = s.ID
        ''')
        print(f'MeetTimes with valid section FK: {cursor.fetchone()[0]}')

        cursor.execute('''
            SELECT COUNT(*)
            FROM Students st
            JOIN Users u ON st.ParentID = u.ID
        ''')
        print(f'Students with valid user FK: {cursor.fetchone()[0]}')

        cursor.execute('''
            SELECT COUNT(*)
            FROM Students st
            LEFT JOIN Advisors a ON st.AdvisorID = a.ID
            WHERE st.ID IS NULL OR a.ID IS NOT NULL
        ''')
        print(f'Students with valid advisor FK/NULL: {cursor.fetchone()[0]}')

        cursor.execute('''
            SELECT COUNT(*)
            FROM Advisors a
            JOIN Users u ON a.ParentID = u.ID
        ''')
        print(f'Advisors with valid user FK: {cursor.fetchone()[0]}')

        cursor.execute('''
            SELECT COUNT(*)
            FROM MajorsAndMinors mm
            JOIN Students st ON mm.ParentID = st.ID
        ''')
        print(f'Majors/Minors with valid student FK: {cursor.fetchone()[0]}')

        cursor.execute('''
            SELECT COUNT(*)
            FROM Interests i
            JOIN Students st ON i.ParentID = st.ID
        ''')
        print(f'Interests with valid student FK: {cursor.fetchone()[0]}')

        cursor.execute('''
            SELECT COUNT(*)
            FROM ChatLogs cl
            JOIN Students st ON cl.ParentID = st.ID
        ''')
        print(f'Chat logs with valid student FK: {cursor.fetchone()[0]}')

        cursor.execute('''
            SELECT COUNT(*)
            FROM RelevantEvents re
            JOIN Students st ON re.ParentID = st.ID
            JOIN Events e ON re.ParentID = e.ID
        ''')
        print(f'Relevant events with valid event/student FK: {cursor.fetchone()[0]}')
    
    except Exception as e:
        raise RuntimeError(
            f"Unexpected error while initializing database: {e}"
        ) from e
    
    finally:
        # Ensure the connection is closed
        if conn:
            conn.close()
