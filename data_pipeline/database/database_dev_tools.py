import sys, os

# Add the project root so `lg_agent` can be imported as a package.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

import json, sqlite3
from lg_agent.database_utils import get_data_with_hierarchy_string

DATABASE = "AdvisorDB.db"

def __connect(database: str = DATABASE):
    conn = sqlite3.connect(database)
    conn.execute('PRAGMA foreign_keys = ON')
    conn.row_factory = sqlite3.Row
    return conn

# Utility function to set up the database with the required tables and schema
def setup_database(database: str = DATABASE):
    with __connect(database) as conn:
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
                LastEventCheck DATETIME NOT NULL DEFAULT '1970-01-01T00:00:00',
                LastSectionStatusCheck DATETIME NOT NULL DEFAULT '1970-01-01T00:00:00',
                ParentID INTEGER NOT NULL UNIQUE,
                FOREIGN KEY (AdvisorID) REFERENCES Advisors(ID)
                    ON DELETE SET NULL,
                FOREIGN KEY (ParentID) REFERENCES Users(ID)
                    ON DELETE CASCADE
            )'''
        )
        # Table for majors and minors for each student, linked to the student via ParentID foreign key and to the MajorsAndMinors table via MajorMinorID foreign key
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS StudentMajorsAndMinors(
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
        print(f"Database '{database}' setup complete with required tables and schema.")

# Utility function to reset the course catalog tables
def reset_course_catalog(database: str = DATABASE):
    with __connect(database) as conn:
        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        # Drop course catalog tables
        cursor.execute('DROP TABLE IF EXISTS Courses')
        cursor.execute('DROP TABLE IF EXISTS CourseRequiredCourses')
        cursor.execute('DROP TABLE IF EXISTS CourseRequiredCourseOptions')
        cursor.execute('DROP TABLE IF EXISTS MiscCourseRequirements')

        # Commit the changes to the database
        conn.commit()
        print("Course catalog tables reset.")

# Utility function to reset the majors and minors catalog tables
def reset_majors_and_minors_catalog(database: str = DATABASE):
    with __connect(database) as conn:
        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        # Drop majors and minors catalog tables
        cursor.execute('DROP TABLE IF EXISTS MajorsAndMinors')
        cursor.execute('DROP TABLE IF EXISTS MajorMinorRequiredCourses')
        cursor.execute('DROP TABLE IF EXISTS MajorMinorRequiredCourseOptions')

        # Commit the changes to the database
        conn.commit()
        print("Majors and minors catalog tables reset.")

# Utility function to reset the terms and courses offered tables
def reset_terms_and_courses(database: str = DATABASE):
    with __connect(database) as conn:
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
def reset_events(database: str = DATABASE):
    with __connect(database) as conn:
        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        # Drop events tables
        cursor.execute('DROP TABLE IF EXISTS Events')
        cursor.execute('DROP TABLE IF EXISTS EventDates')

        # Commit the changes to the database
        conn.commit()

# Utility function to reset the users, advisors, and students tables
def reset_users(database: str = DATABASE):
    with __connect(database) as conn:
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
def reset_all(database: str = DATABASE):
    reset_course_catalog(database)
    reset_majors_and_minors_catalog(database)
    reset_terms_and_courses(database)
    reset_events(database)
    reset_users(database)

def create_triggers(database: str = DATABASE):
    with __connect(database=database) as conn:
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

# Utility function to fetch all results from a query
def fetch_all(cursor: sqlite3.Cursor, query: str, params: tuple = ()):
	cursor.execute(query, params)
	return cursor.fetchall()

# Utility function to populate the course catalog in the database from a JSON file containing course information
def populate_course_catalog(database: str = DATABASE, json_file: str = "courses.json"):
    # TODO: implement this function once we have a JSON file with course info to work with
    pass
    with __connect(database) as conn:
        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        # Reset course catalog tables
        cursor.execute('DROP TABLE IF EXISTS Courses')
        cursor.execute('DROP TABLE IF EXISTS CourseRequiredCourses')
        cursor.execute('DROP TABLE IF EXISTS CourseRequiredCourseOptions')
        cursor.execute('DROP TABLE IF EXISTS MiscCourseRequirements')

        # Commit the changes to the database
        conn.commit()
        print("Course catalog tables reset.")

# Utility function to populate the majors and minors catalog in the database from a JSON file containing major/minor information
def populate_majors_and_minors_catalog(database: str = DATABASE, json_file: str = "majors_and_minors.json"):
    # TODO: implement this function once we have a JSON file with major/minor info to work with
    pass
    with __connect(database) as conn:
        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        # Drop majors and minors catalog tables
        cursor.execute('DROP TABLE IF EXISTS MajorsAndMinors')
        cursor.execute('DROP TABLE IF EXISTS MajorMinorRequiredCourses')
        cursor.execute('DROP TABLE IF EXISTS MajorMinorRequiredCourseOptions')

        # Commit the changes to the database
        conn.commit()
        print("Majors and minors catalog tables reset.")

# Utility function to add a new term and its courses/sections from a JSON file
# TODO: update this to follow new database structure
def add_new_term(database: str = DATABASE, json_file: str = "terms.json"):
    with __connect(database) as conn:
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
def display_term_hierarchy(database: str = DATABASE):
    with __connect(database) as conn:
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