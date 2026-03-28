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

        # Create the course related tables if they do not exist
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS Terms(
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Year INTEGER NOT NULL,
                Season TEXT NOT NULL,
                Number INTEGER
            )'''
        )
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS CoursesOffered(
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Department TEXT NOT NULL,
                Code INTEGER NOT NULL,
                Name TEXT NOT NULL,
                Description TEXT NOT NULL,
                Credits INTEGER NOT NULL,
                ParentID INTEGER NOT NULL,
                FOREIGN KEY (ParentID) REFERENCES Terms(ID)
                    ON DELETE CASCADE
            )'''
        )
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS CourseRequirements(
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Department TEXT NOT NULL,
                Code INTEGER NOT NULL,
                Grade REAL,
                ParentID INTEGER NOT NULL,
                FOREIGN KEY (ParentID) REFERENCES CoursesOffered(ID)
                    ON DELETE CASCADE
            )'''
        )
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS Sections(
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                SectionNum INTEGER NOT NULL,
                Instructor TEXT NOT NULL,
                StartDate DATE NOT NULL,
                EndDate DATE NOT NULL,
                Status TEXT NOT NULL,
                MaxSeats INTEGER NOT NULL,
                SeatsLeft INTEGER NOT NULL,
                Method TEXT NOT NULL,
                Location TEXT,
                ParentID INTEGER NOT NULL,
                FOREIGN KEY (ParentID) REFERENCES CoursesOffered(ID)
                    ON DELETE CASCADE
            )'''
        )
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS MeetTimes(
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Day TEXT NOT NULL,
                StartTime TIME NOT NULL,
                EndTime TIME NOT NULL,
                ParentID INTEGER NOT NULL,
                FOREIGN KEY (ParentID) REFERENCES Sections(ID)
                    ON DELETE CASCADE
            )'''
        )

        # Create user authentication table
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS Users(
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Username TEXT NOT NULL UNIQUE,
                Password TEXT NOT NULL,
                AccountType TEXT NOT NULL
            )'''
        )

        # Create event related tables if they do not exist
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS Events(
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Name TEXT NOT NULL,
                Description TEXT NOT NULL,
                StartDate DATE NOT NULL,
                EndDate DATE NOT NULL,
                StartTime TIME NOT NULL,
                EndTime TIME NOT NULL,
                Location TEXT,
                AddedTimeStamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )'''
        )

        # Create advisor related tables if they do not exist TODO: decide what other info we should add to this
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS Advisors(
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Name TEXT,
                ParentID INTEGER NOT NULL UNIQUE,
                FOREIGN KEY (ParentID) REFERENCES Users(ID)
                    ON DELETE CASCADE
            )'''
        )

        # Create student related tables if they do not exist
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS Students(
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Name TEXT,
                GPA REAL,
                CreditsEarned INTEGER,
                IntendedGraduationTerm TEXT,
                AdvisorID INTEGER,
                LastEventCheck DATETIME,
                LastSectionStatusCheck DATETIME,
                ParentID INTEGER NOT NULL UNIQUE,
                FOREIGN KEY (AdvisorID) REFERENCES Advisors(ID)
                    ON DELETE SET NULL,
                FOREIGN KEY (ParentID) REFERENCES Users(ID)
                    ON DELETE CASCADE
            )'''
        )
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS MajorsAndMinors(
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Title TEXT NOT NULL,
                Type TEXT NOT NULL,
                ParentID INTEGER NOT NULL,
                FOREIGN KEY (ParentID) REFERENCES Students(ID)
                    ON DELETE CASCADE
            )'''
        )
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS Interests(
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Interest TEXT NOT NULL,
                ParentID INTEGER NOT NULL,
                FOREIGN KEY (ParentID) REFERENCES Students(ID)
                    ON DELETE CASCADE
            )'''
        )
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS ChatLogs(
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Log TEXT NOT NULL,
                Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                ParentID INTEGER NOT NULL,
                FOREIGN KEY (ParentID) REFERENCES Students(ID)
                    ON DELETE CASCADE
            )'''
        )
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS RelevantEvents(
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Urgency INTEGER NOT NULL,
                EventID INTEGER NOT NULL,
                ParentID INTEGER NOT NULL,
                FOREIGN KEY (ParentID) REFERENCES Students(ID)
                    ON DELETE CASCADE,
                FOREIGN KEY (EventID) REFERENCES Events(ID)
                    ON DELETE CASCADE
            )'''
        )
        # Table to track which sections each student is tracking for course opening alerts
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS TrackedSections(
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                SectionID INTEGER NOT NULL,
                ParentID INTEGER NOT NULL,
                FOREIGN KEY (ParentID) REFERENCES Students(ID)
                    ON DELETE CASCADE,
            )'''
        )

        # Table for course opening alerts
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS SectionStatusChanges(
                ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                SectionID INTEGER NOT NULL,
                OldStatus TEXT NOT NULL,
                NewStatus TEXT NOT NULL,
                ChangeTime DATETIME NOT NULL,
                FOREIGN KEY (SectionID) REFERENCES Sections(ID)
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

def create_triggers():
    try:
        # Connect to sqlite database
        conn = sqlite3.connect(database)
        conn.execute('PRAGMA foreign_keys = ON')

        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        # Create trigger to log section status changes for course opening alerts
        cursor.execute(
            '''
            CREATE TRIGGER IF NOT EXISTS LogSectionStatusChange
            AFTER UPDATE OF Status ON Sections
            FOR EACH ROW
            WHEN NEW.Status != OLD.Status
            BEGIN
                INSERT INTO SectionStatusChanges (SectionID, OldStatus, NewStatus, ChangeTime)
                VALUES (OLD.ID, OLD.Status, NEW.Status, CURRENT_TIMESTAMP);
            END;
            '''
        )

        # Commit the changes to the database
        conn.commit()
    
    except Exception as e:
        raise RuntimeError(
            f"Failed to create triggers: {e}"
        ) from e
    
    finally:
        # Ensure the connection is closed
        if conn:
            conn.close()

# Utility function to fetch all results from a query
def fetch_all(cursor: sqlite3.Cursor, query: str, params: tuple = ()):
	cursor.execute(query, params)
	return cursor.fetchall()

# Utility function to view the course hierarchy and contents in a readable format
def view_database_course_hierarchy():
    try:
        # Connect to sqlite database
        conn = sqlite3.connect(database)
        conn.execute('PRAGMA foreign_keys = ON')
        conn.row_factory = sqlite3.Row

        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()
        
        terms = cursor.execute(
			'''
			SELECT ID, Year, Season, Number
			FROM Terms
			ORDER BY Year, Season, Number, ID
			''',
		).fetchall()
        
        print(f'Database: {database}')
        print('\n══ COURSE HIERARCHY ══')
        print('Hierarchy: Terms -> CoursesOffered -> (CourseRequirements, Sections -> MeetTimes)\n')
        
        for term in terms:
            summer_part = f' {term["Number"]}' if term['Season'] == 'Summer' and term['Number'] else ''
            print(f'Term {term["ID"]}: {term["Season"]}{summer_part} {term["Year"]}')
            
            courses = cursor.execute(
				'''
				SELECT ID, Department, Code, Description, Credits
				FROM CoursesOffered
				WHERE ParentID = ?
				ORDER BY Department, Code, ID
				''',
				(term['ID'],),
			).fetchall()
            
            if not courses:
                print('  └─ (no courses)')
                continue
            
            for course in courses:
                print(
					f'  ├─ Course {course["ID"]}: '
					f'{course["Department"]} {course["Code"]} '
					f'({course["Credits"]} cr) - {course["Description"]}'
				)
                
                requirements = cursor.execute(
					'''
					SELECT ID, Department, Code, Name, Description, Credits, ParentID
					FROM CourseRequirements
					WHERE ParentID = ?
					ORDER BY ID
					''',
					(course['ID'],),
				).fetchall()

                if requirements:
                    for req in requirements:
                        req_code = req['Code'] if req['Code'] is not None else 'N/A'
                        req_grade = req['Grade'] if req['Grade'] is not None else 'N/A'
                        print(
							f'  │  ├─ Requirement {req["ID"]}: '
							f'{req["Department"]} {req_code} min grade {req_grade}'
						)
                else:
                    print('  │  ├─ (no requirements)')
                
                sections = cursor.execute(
					'''
					SELECT ID, SectionNum, Instructor, MaxSeats, SeatsLeft, Method, Location
					FROM Sections
					WHERE ParentID = ?
					ORDER BY SectionNum, ID
					''',
					(course['ID'],),
				).fetchall()

                if not sections:
                    print('  │  └─ (no sections)')
                    continue
                
                for section in sections:
                    location = section['Location'] if section['Location'] else 'TBD'
                    print(
						f'  │  └─ Section {section["ID"]} '
						f'(#{section["SectionNum"]}): '
						f'{section["Instructor"]}, {section["Method"]}, {location}, '
						f'{section["SeatsLeft"]}/{section["MaxSeats"]} seats left'
					)
                    
                    meet_times = fetch_all(
						cursor,
						'''
						SELECT ID, Day, StartTime, EndTime
						FROM MeetTimes
						WHERE ParentID = ?
						ORDER BY ID
						''',
						(section['ID'],),
					)
                    
                    if meet_times:
                        for meet in meet_times:
                            print(
								f'  │     └─ MeetTime {meet["ID"]}: '
								f'{meet["Day"]} {meet["StartTime"]}-{meet["EndTime"]}'
						    )
                    else:
                        print('  │     └─ (no meet times)')
                
            print()
    
    except Exception as e:
        raise RuntimeError(
            f"Failed to view course hierarchy: {e}"
        ) from e
    
    finally:
        # Ensure the connection is closed
        if conn:
            conn.close()

# Utility function to view the advisor-student hierarchy and contents in a readable format
def view_advisors_to_students_hierarchy():
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

# Utility function to insert basic test data into the database for development/testing purposes
def insert_basic_test_data():
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

setup_database()
insert_basic_test_data()