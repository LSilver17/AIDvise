import sys, os

# Add the path to the root directory to the path if not already there
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

# Add the jsons directory to the path if not already there, 
jsons_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'jsons'))
if jsons_dir not in sys.path:
    sys.path.append(jsons_dir)

import json, sqlite3
from lg_agent.database_utils import get_data_with_hierarchy_string, get_courseID_by_title

COURSE_CATALOG = "qcc_classes.json"
PROGRAMS_CATALOG = "qcc_programs.json"

# Utility function for connecting to database and setting up required pragmas and row factory
def __connect():
    with open(os.path.join(root_dir, "database_config.json"), 'r') as f:
        db_config = json.load(f)
    conn = sqlite3.connect(db_config["database"] + ".db")
    conn.execute('PRAGMA foreign_keys = ON')
    conn.row_factory = sqlite3.Row
    return conn

# Utility function to set up the database with the required tables and schema
def setup_database():
    with __connect() as conn:
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
                Requirements TEXT,
                SemestersOffered TEXT
            )'''
        )

        # Create tables for all programs of study offered at the college
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS ProgramsOfStudy(
                ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                Title TEXT NOT NULL,
                Description TEXT NOT NULL,
                CreditsRequired TEXT NOT NULL,
                Type TEXT NOT NULL CHECK(Type IN ('Certificate', 'Associate in Science', 'Associate in Applied Science', 'Associate in Arts'))
            )'''
        )
        # Table for required courses for each program of study, linked to the program via ParentID foreign key
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS ProgramRequiredCourses(
                ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                ParentID INTEGER NOT NULL,
                FOREIGN KEY (ParentID) REFERENCES ProgramsOfStudy(ID)
                    ON DELETE CASCADE
            )'''
        )
        # Table for options for required courses for each program of study, linked to the requirement via ParentID foreign key and to the course via CourseID foreign key
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS ProgramRequiredCourseOptions(
                ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                CourseID INTEGER NOT NULL,
                ParentID INTEGER NOT NULL,
                FOREIGN KEY (CourseID) REFERENCES Courses(ID)
                    ON DELETE CASCADE,
                FOREIGN KEY (ParentID) REFERENCES ProgramRequiredCourses(ID)
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
                TimeAdded DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
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
                ParentID INTEGER UNIQUE,
                FOREIGN KEY (ParentID) REFERENCES Users(ID)
                    ON DELETE CASCADE
            )'''
        )

        # Table for students, linked to the Users table via ParentID foreign key with a unique constraint to ensure a 1-1 relationship between users and students, and linked to advisors via AdvisorID foreign key with a SET NULL on delete to allow students to remain in the system without an advisor if their advisor is deleted
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS Students(
                ID INTEGER PRIMARY KEY UNIQUE,
                Name TEXT,
                GPA REAL,
                CreditsEarned INTEGER,
                IntendedGraduationTerm TEXT,
                AdvisorID INTEGER,
                LastEventCheck DATETIME NOT NULL DEFAULT '1970-01-01T00:00:00',
                LastSectionStatusCheck DATETIME NOT NULL DEFAULT '1970-01-01T00:00:00',
                ParentID INTEGER UNIQUE,
                FOREIGN KEY (AdvisorID) REFERENCES Advisors(ID)
                    ON DELETE SET NULL,
                FOREIGN KEY (ParentID) REFERENCES Users(ID)
                    ON DELETE SET NULL
            )'''
        )
        # Table for majors and minors for each student, linked to the student via ParentID foreign key and to the ProgramsOfStudy table via ProgramID foreign key
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS StudentProgramsOfStudy(
                ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                ProgramID INTEGER NOT NULL,
                ParentID INTEGER NOT NULL,
                FOREIGN KEY (ProgramID) REFERENCES ProgramsOfStudy(ID)
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
                Timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
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
                AlertStatus TEXT NOT NULL DEFAULT 'Unseen' CHECK(AlertStatus IN ('Unseen', 'Seen')),
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
                    ON DELETE CASCADE
            )'''
        )

        # Table for course opening alerts
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS StudentSectionStatusChanges(
                ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                ChangeID INTEGER NOT NULL,
                AlertStatus TEXT NOT NULL DEFAULT 'Unseen' CHECK(AlertStatus IN ('Unseen', 'Seen')),
                ParentID INTEGER NOT NULL,
                FOREIGN KEY (ParentID) REFERENCES Students(ID)
                    ON DELETE CASCADE,
                FOREIGN KEY (ChangeID) REFERENCES SectionStatusChanges(ID)
                    ON DELETE CASCADE
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
        with open(os.path.join(root_dir, "database_config.json"), 'r') as f:
            db_config = json.load(f)
        print(f"Database '{db_config['database']}' setup complete with required tables and schema.")

# Utility function to reset the course catalog tables
def reset_course_catalog():
    with __connect() as conn:
        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        # Reset course catalog tables
        cursor.execute('DROP TABLE IF EXISTS Courses')

        # Commit the changes to the database
        conn.commit()
        print("Course catalog tables reset.")

# Utility function to reset the programs of study catalog tables
def reset_programs_catalog():
    with __connect() as conn:
        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        # Drop programs of study catalog tables
        cursor.execute('DROP TABLE IF EXISTS ProgramsOfStudy')
        cursor.execute('DROP TABLE IF EXISTS ProgramRequiredCourses')
        cursor.execute('DROP TABLE IF EXISTS ProgramRequiredCourseOptions')

        # Commit the changes to the database
        conn.commit()
        print("Programs of study catalog tables reset.")

# Utility function to reset the terms and courses offered tables
def reset_terms_and_courses():
    with __connect() as conn:
        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        # Drop terms and courses offered tables
        cursor.execute('DROP TABLE IF EXISTS Terms')
        cursor.execute('DROP TABLE IF EXISTS CoursesOffered')
        cursor.execute('DROP TABLE IF EXISTS Sections')
        cursor.execute('DROP TABLE IF EXISTS MeetTimes')

        # Commit the changes to the database
        conn.commit()

# Utility function to view the course hierarchy and contents in a readable format
def reset_events():
    with __connect() as conn:
        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        # Drop events tables
        cursor.execute('DROP TABLE IF EXISTS Events')
        cursor.execute('DROP TABLE IF EXISTS EventDates')

        # Commit the changes to the database
        conn.commit()

# Utility function to reset the users, advisors, and students tables
def reset_users():
    with __connect() as conn:
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

# Utility function to reset all tables in the database except for course catalog tables
def reset_all():
    reset_course_catalog()
    reset_programs_catalog()
    reset_terms_and_courses()
    reset_events()
    reset_users()

# Utility function to create database triggers
def create_triggers():
    with __connect() as conn:
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

        # create trigger to reset last event check and last section status check field of a student entry when its parent id field is changed to null
        cursor.execute(
            '''
            CREATE TRIGGER IF NOT EXISTS ResetCheckFields
            AFTER UPDATE OF ParentID ON Students
            FOR EACH ROW
            WHEN NEW.ParentID IS NULL
            BEGIN
                UPDATE Students
                SET LastEventCheck = '1970-01-01T00:00:00', LastSectionStatusCheck = '1970-01-01T00:00:00'
                WHERE ID = NEW.ID;
            END;
            '''
        )

        # Create trigger to delete relevant events, intresets, tracked sections, and section status changes for a student when the student's ParentID field is updated to null
        cursor.execute(
            '''
            CREATE TRIGGER IF NOT EXISTS DeleteStudentData
            AFTER UPDATE OF ParentID ON Students
            FOR EACH ROW
            WHEN NEW.ParentID IS NULL
            BEGIN
                DELETE FROM RelevantEvents WHERE ParentID = NEW.ID;
                DELETE FROM Interests WHERE ParentID = NEW.ID;
                DELETE FROM TrackedSections WHERE ParentID = NEW.ID;
                DELETE FROM StudentSectionStatusChanges WHERE ParentID = NEW.ID;
            END;
            '''
        )

        # Create trigger to reset last event check field for a student when an interest is added for them
        cursor.execute(
            '''
            CREATE TRIGGER IF NOT EXISTS ResetEventCheckOnInterestChange
            AFTER INSERT ON Interests
            FOR EACH ROW
            BEGIN
                UPDATE Students
                SET LastEventCheck = '1970-01-01T00:00:00'
                WHERE ID = NEW.ParentID;
            END;
            '''
        )

        # Create trigger to reset last event check field for a student when an interest is changed for them
        cursor.execute(
            '''
            CREATE TRIGGER IF NOT EXISTS ResetEventCheckOnInterestChange
            AFTER UPDATE ON Interests
            FOR EACH ROW
            BEGIN
                UPDATE Students
                SET LastEventCheck = '1970-01-01T00:00:00'
                WHERE ID = NEW.ParentID;
            END;
            '''
        )

        # Commit the changes to the database
        conn.commit()

# Utility function to populate the course catalog in the database from a JSON file containing course information (file must be located in the jsons directory)
def populate_course_catalog(json_file: str = COURSE_CATALOG):
    with __connect() as conn:
        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        with open(os.path.join(jsons_dir, json_file), 'r') as f:
            course_data = {"courses": {}}
            course_data['courses'] = json.load(f)
            for course in course_data['courses']:
                # split course code into department and course number
                department, code = course['course_code'].split()

                # split up semesters (e.g. F/S/SU -> F, S, SU) then convert to proper name (e.g. F -> Fall) then combine back into string to store in database
                semesters = course['semesters_offered'].split('/')
                semester_mapping = {
                    'F': 'Fall',
                    'S': 'Spring',
                    'SU': 'Summer',
                    'IN': 'Winter'
                }
                for i, semester in enumerate(semesters):
                    semesters[i] = semester_mapping[semester]
                semesters_offered = '/'.join(semesters)

                cursor.execute(
                    '''
                    INSERT INTO Courses (Department, Code, Name, Description, Credits, Requirements, SemestersOffered)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''',
                    (
                        department,
                        int(code),
                        course['name'],
                        course['description'],
                        course['credits'],
                        course['prerequisites'],
                        semesters_offered
                    )
                )

        # Commit the changes to the database
        conn.commit()
        print("Course catalog populated from JSON file.")

# Utility function to populate the programs of study catalog in the database from a JSON file containing program information
def populate_programs_catalog(json_file: str = PROGRAMS_CATALOG):
    with __connect() as conn:
        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        with open(os.path.join(jsons_dir, json_file), 'r') as f:
            programs_data = {"programs": {}}
            programs_data['programs'] = json.load(f)
            for program in programs_data['programs']:
                cursor.execute(
                    '''
                    INSERT INTO ProgramsOfStudy (Title, Description, CreditsRequired, Type)
                    VALUES (?, ?, ?, ?)
                    ''',
                    (
                        program['name'],
                        program['description'], # TODO: ask noel about where he got those descriptions from
                        program['total_credits'],
                        program['area_of_study']
                    )
                )
                program_id = cursor.lastrowid

                # TODO: Ask Noel about adding the OR for course requirements with multiple options
                previous_requirement_id = None
                has_or = False
                for required_course in program['required_courses']:
                    last_has_or = has_or

                    # check if current course has an OR at the end of its name
                    if required_course['name'].endswith(' OR'):
                        has_or = True
                        required_course['name'] = required_course['name'].rstrip(' OR') # remove the 'OR' from the course name to match the course titles in the database

                    # check if current course works as alternitive for previous one
                    if last_has_or:
                        # add current course as an option for the previous requirement
                        cursor.execute(
                            '''
                            INSERT INTO ProgramRequiredCourseOptions (CourseID, ParentID)
                            VALUES (?, ?)
                            ''',
                            (get_courseID_by_title(required_course['name']), previous_requirement_id,)
                        )
                    else:
                        # add current course as a new requirement
                        cursor.execute(
                            '''
                            INSERT INTO ProgramRequiredCourses (ParentID)
                            VALUES (?)
                            ''',
                            (program_id,)
                        )
                        requirement_id = cursor.lastrowid

                        # add current course as an option for the new requirement
                        cursor.execute(
                            '''
                            INSERT INTO ProgramRequiredCourseOptions (CourseID, ParentID)
                            VALUES (?, ?)
                            ''',
                            (get_courseID_by_title(required_course['name']), requirement_id)
                        )

                        previous_requirement_id = requirement_id

        # Commit the changes to the database
        conn.commit()
        print("Programs of study catalog populated from JSON file.")

# Utility function to add a new term and its courses/sections from a JSON file
# TODO: update this to follow new database structure
def add_new_term(json_file: str = "terms.json"):
    with __connect() as conn:
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

# Utility function to display the hierarchy of terms, courses, sections, and meet times in the database for debugging purposes
def display_term_hierarchy():
    with __connect() as conn:
        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        # Get id of all terms in the database
        terms = cursor.execute('SELECT ID FROM Terms').fetchall()

        # Display the hierarchy of each term and its courses/sections/meet times using the get_data_with_hierarchy_string utility function
        for term in terms:
            term_data = get_data_with_hierarchy_string(
                cursor,
                "Terms",
                term['ID'],
            )
            print(term_data)

# if this script is run directly, set up the database and display the term hierarchy for debugging purposes
if __name__ == '__main__':
    setup_database()
    create_triggers()
