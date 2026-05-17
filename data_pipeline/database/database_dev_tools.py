"""
Copyright 2026 Luca Silver

This module provides development tools for managing the SQLite database used by the advising application. It includes functions to set up the database schema, create necessary triggers, populate tables from JSON files, and reset specific groups of tables during development.

Functions:
-  ``__connect()``: Internal function to establish a connection to the SQLite database with appropriate configuration.
- ``aconnect()``: Async variant of the database connection function using aiosqlite.
- ``setup_database()``: Creates the database schema with all required tables.
- ``create_triggers()``: Creates database triggers for logging section status changes and resetting student check fields.
- ``populate_course_catalog(json_file)``: Loads course data from a JSON file and populates the ``Courses`` table.
- ``populate_programs_catalog(json_file)``: Loads program of study data from a JSON file and populates the ``ProgramsOfStudy`` and related requirement tables.
- ``add_new_term(json_file)``: Inserts a new term and its course offerings, sections, and meet times from a JSON file.
- ``add_students_from_json(json_file)``: Loads student data from a JSON file and populates the ``Students`` table and courses taken table.
- Reset functions:
    - ``reset_course_catalog()``: Drops course-related tables.
    - ``reset_programs_catalog()``: Drops program-of-study related tables.
    - ``reset_students_and_advisors()``: Drops the ``Students`` and ``Advisors`` tables.
    - ``reset_terms_and_courses()``: Drops term- and offering-related tables.
    - ``reset_events()``: Drops event-related tables.
    - ``reset_users()``: Drops the ``Users`` table (cascades to related data).
    - ``reset_all()``: Calls all reset functions in sequence to wipe the database.

Reset functions can be used in conjunction with ``setup_database()`` to update the schema and clear out old data before repopulating from JSON. Exercise caution when using reset functions as they permanently delete data.
This file can also be run as a script to execute the following sequence of operations: set up the database schema, create triggers, populate the course catalog and programs catalog from their respective JSON files, and add a new term with offerings from its JSON file.
"""

import sys, os

# Add the path to the root directory to the path if not already there
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# Add the jsons directory to the path if not already there, 
JSONS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'jsons'))
if JSONS_DIR not in sys.path:
    sys.path.append(JSONS_DIR)

import json, sqlite3, aiosqlite
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from lg_agent.database_utils import get_courseID_by_code

load_dotenv(os.path.join(ROOT_DIR, '.env'))

EMAIL_TEST_MODE = os.getenv("EMAIL_TEST_MODE", "False").lower() == "true"
if EMAIL_TEST_MODE:
    TEST_EMAIL_ADDRESS = os.getenv("TEST_EMAIL_ADDRESS", "error")
    if TEST_EMAIL_ADDRESS == "error":
        raise ValueError("EMAIL_TEST_MODE is set to True but TEST_EMAIL_ADDRESS is not set in the environment variables. Please set TEST_EMAIL_ADDRESS to a valid email address to use as the recipient for all emails in test mode.")

def __connect():
    """Create and return a configured SQLite connection to the project's database.

    Reads the database filename from ``config.json`` in the repository root, opens a connection to <database>.db, enables foreign key enforcement, and sets the connection ``row_factory`` to ``sqlite3.Row`` so query results behave like mapping objects.

    Returns:
        sqlite3.Connection: An open SQLite connection with pragma and row factory set.
    """
    with open(os.path.join(ROOT_DIR, "config.json"), 'r') as f:
        CONFIG = json.load(f)
        DB_CONFIG = CONFIG["database_config"]
    conn = sqlite3.connect(DB_CONFIG["db_name"] + ".db")
    conn.execute('PRAGMA foreign_keys = ON')
    conn.row_factory = sqlite3.Row
    return conn

@asynccontextmanager
async def aconnect():
    """Async variant of __connect using aiosqlite.

    Yields an `aiosqlite.Connection` with foreign keys enabled and the same
    row_factory as the synchronous connector. Use `async with aconnect() as conn:`
    in async contexts.
    """
    with open(os.path.join(ROOT_DIR, "config.json"), 'r') as f:
        CONFIG = json.load(f)
        DB_CONFIG = CONFIG["database_config"]
    async with aiosqlite.connect(DB_CONFIG["db_name"] + ".db") as conn:
        await conn.execute('PRAGMA foreign_keys = ON')
        conn.row_factory = sqlite3.Row
        yield conn

def setup_database():
    """Create the project's database schema.

    This function opens a connection using :pyfunc:`__connect` and creates all of the tables used by the project (courses, terms, sections, meet times, users, verification tokens, students, advisors, programs of study, program requirement tables, events and related tables). Each CREATE TABLE uses ``IF NOT EXISTS`` so the operation is idempotent.

    The function commits the schema changes and prints a confirmation message indicating which database file was initialized.
    """
    with __connect() as conn:
        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        # Table with all courses offered by the college
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS Courses(
                ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                Department TEXT NOT NULL,
                Code INTEGER NOT NULL,
                Name TEXT,
                Description TEXT,
                Credits INTEGER,
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
                CreditsRequired TEXT,
                Type TEXT CHECK(Type IN ('Certificate', 'Associate in Science', 'Associate in Applied Science', 'Associate in Arts'))
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
                CourseID INTEGER,
                Elective TEXT,
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
                AccountType TEXT NOT NULL CHECK(AccountType IN ('Student', 'Advisor')),
                VerificationToken TIMESTAMP DEFAULT NULL
            )'''
        )
        # Table for verification tokens for account creation email authentication
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS VerficationToken(
                identifier TEXT PRIMARY KEY UNIQUE,
                token TEXT NOT NULL,
                expires TIMESTAMP NOT NULL
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
                Email TEXT NOT NULL,
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
                Email TEXT NOT NULL,
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
                Grade TEXT NOT NULL CHECK(Grade IN ('A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F', 'X', 'W', 'NR', "IP")),
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
        with open(os.path.join(ROOT_DIR, "config.json"), 'r') as f:
            CONFIG = json.load(f)
        print(f"Database '{CONFIG['database_config']['db_name']}' setup complete with required tables and schema.")

def create_triggers():
    """Create database triggers used by the application.
    
    The following triggers are created (if they do not already exist):
    - ``LogSectionStatusChange``: inserts a row in ``SectionStatusChanges`` when a section's ``Status`` column changes.
    - ``ResetCheckFields``: resets a student's ``LastEventCheck`` and ``LastSectionStatusCheck`` timestamps when their ``ParentID`` becomes NULL.
    - ``DeleteStudentData``: deletes related rows (relevant events, interests, tracked sections, student alerts) when a student's ``ParentID`` is set to NULL.
    - ``ResetEventCheckOnInterestChange`` (insert and update variants): reset a student's ``LastEventCheck`` when interests are inserted or updated.
    """
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
            CREATE TRIGGER IF NOT EXISTS ResetEventCheckOnInterestChangeInsert
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
            CREATE TRIGGER IF NOT EXISTS ResetEventCheckOnInterestUpdate
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

def populate_course_catalog(json_file: str = "course_catalog.json"):
    """Load catalog of course from a JSON file and insert them into ``Courses``.

    The JSON file is expected to be located in the repository's ``jsons`` directory. Each entry should contain at minimum the fields used below: ``course_code`` (format: "DPT NUM"), ``name``, ``description``, ``credits``, ``prerequisites``, and ``semesters_offered`` (e.g. "F/S/SU").

    The function converts ``course_code`` into the ``Department`` and numeric ``Code`` columns, maps semester initials to full names (F -> Fall, S -> Spring, SU -> Summer, IN -> Winter), and inserts a row into the ``Courses`` table for each course. Operation is committed at the end.

    Args:
        json_file (str): Filename in the ``jsons`` directory to load. Defaults to ``course_catalog.json``.

    Notes:
        If ``semesters_offered`` is empty/falsey in the input, ``SemestersOffered`` is stored as ``NULL`` in the database.
    """

    with __connect() as conn:
        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        with open(os.path.join(JSONS_DIR, json_file), 'r') as f:
            course_data = {"courses": {}}
            course_data['courses'] = json.load(f)
            for course in course_data['courses']:
                # Validate required course fields
                required_fields = ['course_code', 'name', 'description', 'credits', 'prerequisites']
                missing_fields = [field for field in required_fields if field not in course]
                if missing_fields:
                    print(f"Skipping course: missing required fields {missing_fields}")
                    continue

                # split course code into department and course number
                try:
                    department, code = str(course['course_code']).split()
                except ValueError:
                    print(f"Invalid course code format: {course.get('course_code')}. Skipping course.")
                    continue

                # split up semesters (e.g. F/S/SU -> F, S, SU) then convert to proper name (e.g. F -> Fall) then combine back into string to store in database
                if course.get('semesters_offered'):
                    semesters = str(course['semesters_offered']).split('/')
                    semester_mapping = {
                        'F': 'Fall',
                        'S': 'Spring',
                        'SU': 'Summer',
                        'IN': 'Winter'
                    }
                    try:
                        for i, semester in enumerate(semesters):
                            semesters[i] = semester_mapping.get(semester, semester)
                        semesters_offered = '/'.join(semesters)
                    except (ValueError, KeyError) as e:
                        print(f"Error processing semesters for {course.get('course_code')}: {e}")
                        semesters_offered = None
                else:
                    semesters_offered = None
                
                cursor.execute(
                    '''
                    INSERT INTO Courses (Department, Code, Name, Description, Credits, Requirements, SemestersOffered)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''',
                    (
                        department,
                        int(code),
                        course.get('name'),
                        course.get('description'),
                        course.get('credits'),
                        course.get('prerequisites'),
                        semesters_offered
                    )
                )
        # Commit the changes to the database
        conn.commit()
        print("Course catalog populated from JSON file.")

def populate_programs_catalog(json_file: str = "qcc_programs.json"):
    """Load programs of study from JSON and populate ``ProgramsOfStudy`` and related requirement tables.

    The input JSON (in the ``jsons`` directory) should contain program records with fields such as ``name``, ``description``, ``total_credits``, ``area_of_study``, and ``required_courses``. Each program is inserted into ``ProgramsOfStudy`` and program requirements are split into rows in ``ProgramRequiredCourses`` and ``ProgramRequiredCourseOptions``.

    Args:
        json_file (str): Filename in the ``jsons`` directory to load. Defaults to ``qcc_programs.json``.

    Notes:
        If a required course string ends with ``" OR"``, it is treated as an alternative to the previous requirement and inserted into the ``ProgramRequiredCourseOptions`` table.
    """
    with __connect() as conn:
        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        with open(os.path.join(JSONS_DIR, json_file), 'r') as f:
            programs_data = {"programs": {}}
            programs_data['programs'] = json.load(f)
            for program in programs_data['programs']:
                # Validate required program fields
                required_fields = ['name', 'description', 'total_credits', 'area_of_study', 'required_courses']
                missing_fields = [field for field in required_fields if field not in program]
                if missing_fields:
                    print(f"Skipping program: missing required fields {missing_fields}")
                    continue

                cursor.execute(
                    '''
                    INSERT INTO ProgramsOfStudy (Title, Description, CreditsRequired, Type)
                    VALUES (?, ?, ?, ?)
                    ''',
                    (
                        program.get('name'),
                        program.get('description'),
                        program.get('total_credits'),
                        program.get('area_of_study')
                    )
                )
                program_id = cursor.lastrowid

                # TODO: Ask Noel about adding the OR for course requirements with multiple options
                previous_requirement_id = None
                has_or = False
                required_courses = program.get('required_courses', [])
                if not isinstance(required_courses, list):
                    print(f"Invalid required_courses format for program '{program.get('name')}'. Skipping requirements.")
                    required_courses = []
                
                for required_course in required_courses:
                    last_has_or = has_or

                    # check if current course has an OR at the end of its name
                    if str(required_course).endswith(' OR'):
                        has_or = True
                        required_course = str(required_course).rstrip(' OR') # remove the 'OR' from the course name to match the course titles in the database

                    # check if current course works as alternitive for previous one
                    if last_has_or:
                        if "Elective" in required_course or len(str(required_course)) == 3:
                            # if the required course allows anything in a specific department or elective type
                            cursor.execute(
                                '''
                                INSERT INTO ProgramRequiredCourseOptions (Elective, ParentID)
                                VALUES (?, ?)
                                ''',
                                (required_course, previous_requirement_id,)
                            )
                        else:
                            cursor.execute(
                                '''
                                INSERT INTO ProgramRequiredCourseOptions (CourseID, ParentID)
                                VALUES (?, ?)
                                ''',
                                (get_courseID_by_code(cursor, required_course), previous_requirement_id,)
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
                        if "Elective" in required_course or len(str(required_course)) == 3:
                            # if the required course allows anything in a specific department or elective type
                            cursor.execute(
                                '''
                                INSERT INTO ProgramRequiredCourseOptions (Elective, ParentID)
                                VALUES (?, ?)
                                ''',
                                (required_course, requirement_id)
                            )
                        else:
                            cursor.execute(
                                '''
                                INSERT INTO ProgramRequiredCourseOptions (CourseID, ParentID)
                                VALUES (?, ?)
                                ''',
                                (get_courseID_by_code(cursor, required_course), requirement_id)
                            )

                        previous_requirement_id = requirement_id

        # Commit the changes to the database
        conn.commit()
        print("Programs of study catalog populated from JSON file.")

def add_new_term(json_file: str = "term_data.json"):
    """Insert a new term and all of its course offerings, sections, and meet times from a JSON export.

    The JSON must be located in the ``jsons`` directory and contain at least one term object with the keys: ``Year``, ``Season``, ``Num`` and a ``CoursesOffered`` list. Each course offering should include fields used below such as ``Department``, ``Code``, ``SectionNum``, ``Instructor``, ``StartDate``, ``EndDate``, ``Status``, ``MaxSeats``, ``SeatsLeft``, ``Method``, ``Location`` and ``MeetTimes``.

    Behavior:
    - Inserts a row into ``Terms`` and uses the inserted term ID as the ``ParentID`` for ``CoursesOffered`` rows.
    - Skips course offerings when the base course cannot be found in ``Courses`` (logs a message and continues).
    - Parses the ``MeetTimes`` string to split day initials and start/end times, converts AM/PM times to 24-hour format, and inserts one ``MeetTimes`` row per day.

    Args:
        json_file (str): Filename in the ``jsons`` directory to load. Defaults to ``term_data.json``.
    """
    with __connect() as conn:
        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        term_data = {"term": {}}

        # Load term data from JSON file
        with open(os.path.join(JSONS_DIR, json_file), 'r') as f:
            term_data['term'] = json.load(f)

        # Validate term data structure
        if not term_data['term'] or not isinstance(term_data['term'], list):
            raise ValueError("Invalid term data format: term must be a non-empty list")
        
        term = term_data['term'][0]
        
        # Validate required term fields
        required_term_fields = ['Year', 'Season', 'Num', 'CoursesOffered']
        missing_fields = [field for field in required_term_fields if field not in term]
        if missing_fields:
            raise ValueError(f"Missing required term fields: {missing_fields}")

        # add the new term to the Terms table and get its ID to use as the ParentID for the courses.
        cursor.execute(
            '''
            INSERT INTO Terms (Year, Season, Number)
            VALUES (?, ?, ?)
            ''',
            (
                term.get('Year'),
                term.get('Season'),
                term.get('Num')
            )
        )
        term_id = cursor.lastrowid

        # Add the courses for the new term to the CoursesOffered table, linking them to the term via ParentID
        for course in term.get('CoursesOffered', []):
            # Validate required course fields
            required_course_fields = ['Department', 'Code', 'SectionNum', 'Instructor', 'StartDate', 'EndDate', 'Status', 'MaxSeats', 'SeatsLeft', 'Method', 'MeetTimes']
            missing_fields = [field for field in required_course_fields if field not in course]
            if missing_fields:
                print(f"Skipping course: missing required fields {missing_fields}")
                continue

            #check if course already exists for the term to avoid duplicates
            existing_course = cursor.execute(
                '''
                SELECT co.ID
                FROM CoursesOffered as co Join Courses as c ON co.CourseID = c.ID
                WHERE c.Department = ? AND c.Code = ? AND co.ParentID = ?
                ''',
                (course.get('Department'), course.get('Code'), term_id)
            ).fetchone()

            # if the course doesn't already exist for the term, insert it into the CoursesOffered table with the appropriate ParentID linking it to the term
            if not existing_course:
                # get course ID from Courses table to link to CoursesOffered table
                course_code = f"{course.get('Department')} {course.get('Code')}"
                course_id = get_courseID_by_code(cursor, course_code)

                if not course_id:
                    print(f"no course id found for course code {course_code}, skipping course offering for {course_code} in term {term.get('Season')} {term.get('Year')}")
                    continue

                cursor.execute(
                    '''
                    INSERT INTO CoursesOffered (CourseID, ParentID)
                    VALUES (?, ?)
                    ''',
                    (course_id, term_id)
                )

            # add the specific section of the course to the Sections table, linking it to the course via ParentID
            try:
                cursor.execute(
                    '''
                    INSERT INTO Sections (SectionNum, Instructor, StartDate, EndDate, Status, MaxSeats, SeatsLeft, Method, Location, ParentID)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''',
                    (
                        int(course.get('SectionNum')),
                        course.get('Instructor'),
                        course.get('StartDate'),
                        course.get('EndDate'),
                        course.get('Status'),
                        course.get('MaxSeats'),
                        course.get('SeatsLeft'),
                        course.get('Method'),
                        course.get('Location'),
                        (existing_course['ID'] if existing_course else cursor.lastrowid)
                    )
                )
            except (ValueError, TypeError) as e:
                print(f"Error inserting section for course {course.get('Code')}: {e}")
                continue

            section_id = cursor.lastrowid
            
            # seperate days from times since the JSON format has them combined and we need to split them to fit our schema
            meet_times = course.get('MeetTimes')
            if meet_times and not meet_times == "00:00-00:00AM":
                try:
                    day_initials, time_unsplit = str(meet_times).split(maxsplit=1)
                    start_time = time_unsplit[:5]
                    start_time_am_pm = None
                    end_time_am_pm = None
                    if time_unsplit[5] == '-': # time like nn:nn-nn:nnAM/PM
                        end_time = time_unsplit[6:11] # get end time by taking the substring after the '-' and before the AM/PM indicator
                        end_time_am_pm = time_unsplit[11:13] # get AM/PM indicator for end time by taking the last 2 characters of the time string
                    else: # time like nn:nnAM/PM-nn:nnAM/PM
                        start_time_am_pm = time_unsplit[5:7] # get AM/PM indicator for start time by taking the 2 characters after the start time
                        end_time = time_unsplit[8:13] # get end time by taking the substring after the start time and its AM/PM indicator and before the end time's AM/PM indicator
                        end_time_am_pm = time_unsplit[13:15] # get AM/PM indicator for end time by taking the last 2 characters of the time string

                    # convert start and end times to 24 hour format based on the AM/PM indicators
                    if start_time_am_pm == 'PM':
                        if start_time[:2] != '12':
                            start_time = str(int(start_time[:2]) + 12) + start_time[2:]
                    elif start_time_am_pm == 'AM':
                        if start_time[:2] == '12':
                            start_time = '00' + start_time[2:]
                    
                    if end_time_am_pm == 'PM':
                        if end_time[:2] != '12':
                            end_time = str(int(end_time[:2]) + 12) + end_time[2:]
                    elif end_time_am_pm == 'AM':
                        if end_time[:2] == '12':
                            end_time = '00' + end_time[2:]

                    # Seperate each day initiall from the string of day initials
                    day_list = list(day_initials)

                    # Convert day initials to full day names
                    day_mapping = {
                        'M': 'Monday',
                        'T': 'Tuesday',
                        'W': 'Wednesday',
                        'R': 'Thursday',
                        'F': 'Friday',
                        'S': 'Saturday'
                    }
                    
                    try:
                        for i, day_initial in enumerate(day_list):
                            if day_initial not in day_mapping:
                                print(f"Invalid day initial found: {day_initial}")
                                continue
                            day_list[i] = day_mapping[day_initial]
                    except (KeyError, TypeError) as e:
                        print(f"Invalid day initial found: {e}")
                        continue

                    # for each day, insert a meet time entry into the MeetTimes table linked to the section via ParentID
                    for day in day_list:
                        cursor.execute(
                            '''
                            INSERT INTO MeetTimes (Day, StartTime, EndTime, ParentID)
                            VALUES (?, ?, ?, ?)
                            ''',
                            (day, start_time, end_time, section_id)
                    )
                except ValueError as e:
                    print(f"Error processing meet times for course {course.get('Code')}: {e}")
                    continue
        # Commit the changes to the database
        conn.commit()

def add_students_from_json(json_file: str):
    """Insert student accounts, course histories, and declared programs from a JSON file into the database.

    Expected JSON structure (per student):
    - ``ID``: numeric student identifier
    - ``Name``: student full name
    - ``Email``: student email address
    - ``GPA``: floating point GPA
    - ``CreditsEarned``: integer
    - ``IntendedGraduationTerm``: string
    - ``Advisor``: (optional) advisor name used to look up an Advisors row
    - ``CoursesTaken``: list of objects with ``CourseCode`` (e.g. "CSC 101") and ``Grade``
    - ``ProgramsOfStudy``: list of program title strings

    Behavior:
    - Inserts a row into ``Students`` for each student.
    - For each ``CoursesTaken`` entry, resolves the course via :pyfunc:`lg_agent.database_utils.get_courseID_by_code` and inserts a ``CoursesTaken`` row. If a course cannot be found, the course is skipped and a message is printed.
    - Associates programs with the student if the program title exists in ``ProgramsOfStudy``.

    Args:
        json_file (str): Filename in the ``jsons`` directory to load.
    """
    with __connect() as conn:
        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        student_data = {"students": []}

        # Load student data from JSON file
        with open(os.path.join(JSONS_DIR, json_file), 'r') as f:
            student_data['students'] = json.load(f)

        for student in student_data['students']:
            # Validate required student fields exist
            required_fields = ['ID', 'Name', 'Email', 'GPA', 'CreditsEarned', 'IntendedGraduationTerm']
            missing_fields = [field for field in required_fields if field not in student]
            if missing_fields:
                print(f"Skipping student: missing required fields {missing_fields}")
                continue

            # check if advisor field is present for the student
            if "Advisor" in student:
                advisor_name = student['Advisor']
                advisor_id = cursor.execute('SELECT ID FROM Advisors WHERE Name = ?', (advisor_name,)).fetchone()
                if advisor_id:
                    advisor_id = advisor_id['ID']
                else:
                    print(f"Advisor '{advisor_name}' not found in database. Setting AdvisorID to null for student '{student['Name']}'.")
                    advisor_id = None
            else:
                advisor_id = None

            if EMAIL_TEST_MODE:
                email = TEST_EMAIL_ADDRESS
            else:
                email = student['Email']
            
            # add the new student to the Students table
            try:
                cursor.execute(
                    '''
                    INSERT INTO Students (ID, Name, Email, GPA, CreditsEarned, IntendedGraduationTerm, AdvisorID)

                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''',
                    (
                        student['ID'],
                        student['Name'],
                        email,
                        student['GPA'],
                        student['CreditsEarned'],
                        student['IntendedGraduationTerm'],
                        advisor_id
                    )
                )
                student_id = cursor.lastrowid

                # Process courses taken if present
                course_history = student.get('CoursesTaken', [])
                for course in course_history:
                    course_code = course.get('CourseCode')
                    grade = course.get('Grade')
                    if not course_code or not grade:
                        print(f"Skipping course entry for student '{student['Name']}': missing CourseCode or Grade")
                        continue
                    
                    course_id = get_courseID_by_code(conn, course_code)
                    if not course_id:
                        print(f"Course '{course_code}' not found in database. Skipping this course for student '{student['Name']}'.")
                        continue

                    cursor.execute(
                        '''
                        INSERT INTO CoursesTaken (CourseID, Grade, ParentID)
                        VALUES (?, ?, ?)
                        ''',
                        (course_id, grade, student_id)
                    )

                # Process programs of study if present
                programs_of_study = student.get('ProgramsOfStudy', [])
                for program in programs_of_study:
                    program_id = cursor.execute('SELECT ID FROM ProgramsOfStudy WHERE Title = ?', (program,)).fetchone()
                    if program_id:
                        program_id = program_id['ID']
                        cursor.execute(
                            '''
                            INSERT INTO StudentProgramsOfStudy (ProgramID, ParentID)
                            VALUES (?, ?)
                            ''',
                            (program_id, student_id)
                        )
                    else:
                        print(f"Program '{program}' not found in database. Skipping this program for student '{student['Name']}'.")
            except sqlite3.IntegrityError as e:
                print(f"Error adding student '{student['Name']}' to database: {e}. Skipping this student.")
                continue

        # Commit the changes to the database
        conn.commit()
        print(f"Student '{student['Name']}' added to database from JSON file.")

def add_advisors_from_json(json_file: str):
    """Insert advisor accounts from a JSON file into the database.

    Expected JSON structure (per advisor):
    - ``Name``: advisor full name
    - ``Email``: advisor email address

    Behavior:
    - Inserts a row into ``Advisors`` for each advisor, linked to a user account in ``Users``. If an advisor with the same name already exists, it is skipped and a message is printed.

    Args:
        json_file (str): Filename in the ``jsons`` directory to load.
    """
    with __connect() as conn:
        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        advisor_data = {"advisors": []}

        # Load advisor data from JSON file
        with open(os.path.join(JSONS_DIR, json_file), 'r') as f:
            advisor_data['advisors'] = json.load(f)

        for advisor in advisor_data['advisors']:
            required_fields = ['Name', 'Email']
            missing_fields = [field for field in required_fields if field not in advisor]
            if missing_fields:
                print(f"Skipping advisor: missing required fields {missing_fields}")
                continue
            # check if an advisor with the same name already exists in the database
            existing_advisor = cursor.execute('SELECT ID FROM Advisors WHERE Name = ?', (advisor['Name'],)).fetchone()
            if existing_advisor:
                print(f"Advisor '{advisor['Name']}' already exists in database. Skipping this advisor.")
                continue

            if EMAIL_TEST_MODE:
                email = TEST_EMAIL_ADDRESS
            else:
                email = advisor['Email']

            # add the new advisor to the Advisors table
            try:
                cursor.execute(
                    '''
                    INSERT INTO Advisors (Name, Email)
                    VALUES (?, ?)
                    ''',
                    (
                        advisor['Name'],
                        email
                    )
                )
            except sqlite3.IntegrityError as e:
                print(f"Error adding advisor '{advisor['Name']}' to database: {e}. Skipping this advisor.")
                continue

        # Commit the changes to the database
        conn.commit()
        print(f"Advisors added to database from JSON file.")

def reset_course_catalog():
    """Drop the ``Courses`` table if it exists.

    This can be used in conjunction with setup_database() to update the course catalog schema or to clear out old course data before repopulating from JSON.

    Warnings: 
        This permanently removes course catalog data.
    """
    with __connect() as conn:
        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        # Reset course catalog tables
        cursor.execute('DROP TABLE IF EXISTS Courses')

        # Commit the changes to the database
        conn.commit()
        print("Course catalog tables reset.")

def reset_programs_catalog():
    """Drop program-of-study related tables: ``ProgramsOfStudy``, ``ProgramRequiredCourses``, and ``ProgramRequiredCourseOptions``.

    This can be used in conjunction with setup_database() to update the programs catalog schema or to clear out old program and requirement data before repopulating from JSON.

    Warnings: 
        This permanently removes programs and requirement data.
    """
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

def reset_students_and_advisors():
    """Drop the ``Students`` and ``Advisors`` tables if they exist.

    This can be used in conjunction with setup_database() to update the student/advisor schema or to clear out old student and advisor data before repopulating from JSON.

    Warnings: 
        This permanently removes student and advisor records.
    """
    with __connect() as conn:
        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        # drop students and advisors tables
        cursor.execute('DROP TABLE IF EXISTS Students')
        cursor.execute('DROP TABLE IF EXISTS Advisors')

        # Commit the changes to the database
        conn.commit()
        print("Students and advisors tables reset.")

def reset_terms_and_courses():
    """Drop term- and offering-related tables: ``Terms``, ``CoursesOffered``, ``Sections``, and ``MeetTimes``.

    This can be used in conjunction with setup_database() to update the term and course offering schema or to clear out old scheduling data before repopulating from JSON.

    Warnings: 
        This permanently removes term offerings and section scheduling data.
    """
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

def reset_events():
    """Drop the ``Events`` and ``EventDates`` tables if they exist.

    This can be used in conjunction with setup_database() to update the events schema or to clear out old event data before repopulating.

    Warnings: 
        This permanently removes event definitions and dates.
    """
    with __connect() as conn:
        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        # Drop events tables
        cursor.execute('DROP TABLE IF EXISTS Events')
        cursor.execute('DROP TABLE IF EXISTS EventDates')

        # Commit the changes to the database
        conn.commit()

def reset_users():
    """Drop the ``Users`` table if it exists.

    This can be used in conjunction with setup_database() to update the user account schema or to clear out old user data before repopulating.

    Warnings:
        This permanently removes user accounts and all related data (interests, relevant events, tracked sections, and course opening alerts) due to the ON DELETE CASCADE foreign key constraints.
    """
    with __connect() as conn:
        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()
        
        # Drop users, advisors, and students tables
        cursor.execute('DROP TABLE IF EXISTS Users')
        
        # Commit the changes to the database
        conn.commit()

def reset_all():
    """Reset all major database groups by dropping their tables.

    This is a convenience wrapper that calls the individual reset functions in the following order: course catalog, programs catalog, terms and courses, events, and users. Use with extreme caution — this operation effectively wipes the application's data.
    This can be used in conjunction with setup_database() to update the entirety of the database schema and clear out all data before repopulating from JSON.

    Warnings:
        This operation effectively wipes the application's data.
    """
    reset_course_catalog()
    reset_programs_catalog()
    reset_terms_and_courses()
    reset_events()
    reset_users()
    print("All tables in the database have been reset.")

if __name__ == '__main__':
    setup_database()
    create_triggers()
    populate_course_catalog("course_catalog_plus.json")
    populate_programs_catalog("qcc_programs_plus.json")
    add_new_term()
