"""
Copyright 2026 Luca Silver

Contains various utility functions for interacting with the registration database.

Functions:
- `get_courseID_by_code`: Return the database course ID matching a course code.
- `get_courseID_by_title`: Return the database course ID for a given course title.
- `get_coops`: Return a list of course IDs for all 'Cooperative Work Experience' entries.
- `get_courseIDs_by_filters`: Return a list of course IDs that match the provided CourseFilters.
- `get_course_info_by_id`: Return course metadata for a given course ID.
- `get_course_description_by_id`: Return the textual description for a course identified by `course_id`.
- `get_sectionIDs_by_filters`: Return a list of section IDs that match the provided SectionFilters.
- `get_section_info_by_id`: Return section-level metadata for the provided section ID.
- `get_upcoming_events`: Return a list of upcoming events with their dates.
- `get_event_dates_by_name`: Return the dates for a specified event.
- `get_student_basic_info`: Return basic profile information for a given student ID, including their name, advisor, GPA, total credits, and programs of study.
- `get_student_course_history`: Return the course history for a given student ID, including course codes, titles, and grades.
- `get_student_interests`: Return a list of interests for a given student ID.
- `get_student_tracked_sections`: Return a list of section IDs that the student is currently tracking for openings.
- `get_program_requirements_by_title`: Return a list of course IDs that are requirements for a given program of study.
- `insert_student_interest`: Insert a new interest for a student.
- `insert_student_tracked_section`: Insert a new section to track for openings for a student.
- `get_data_with_hierarchy`: Return data from a specified table along with related data from parent and child tables to provide context for database entries.
- `_format_hierarchy_node`: Helper function to recursively format a hierarchy node and its children into a nested dictionary structure.
- `hierarchy_data_to_string`: Convert the nested dictionary structure returned by `get_data_with_hierarchy` into a readable string format for easier interpretation of hierarchical relationships in the database.
- `get_data_with_hierarchy_string`: Wrapper function that combines `get_data_with_hierarchy` and `hierarchy_data_to_string` to directly return the hierarchical data as a formatted string.
- `get_ids_by_field_value`: Return a list of IDs from a specified table where a given field matches a specified value.
- `get_ids_by_parent`: Return a list of IDs from a specified table where the ParentID matches a specified value.
- `get_students_by_advisor`: Return a list of student IDs for students who have a specified advisor.
"""

import sys, os

# adds lg_agent directory to system path if not already there
PARENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PARENT_DIR not in sys.path:
    sys.path.append(PARENT_DIR)

from lg_agent.utilities import schemas
import sqlite3

def get_courseID_by_code(cursor: sqlite3.Cursor, course_code: str) -> str:
    """Return the database course ID matching a course code.

    Accepts course codes in either spaced format ("DPT NUM") or compact format ("DPTNUM").

    Args:
        sqlite3.Cursor cursor: cursor object connected to the registration database.
        str course_code: Course code to look up.
            Format: "DPT NUM" | "DPTNUM" (eg. "MAT 101" or "MAT101").

    Returns:
        str: The matching course ID as stored in the `Courses` table.
            Format if found: Primary key value from `Courses.ID` column corresponding to the provided course code. (eg. "12345")
            Note: If no course is found with that code, returns ``None``.
    """
    # check if which format the course code is in (e.g. "CSC 101" vs "CSC101") and split accordingly
    if " " in course_code:
        # split by space
        department, number = course_code.split()
    else:
        # split by the point where the digits start
        for i, char in enumerate(course_code):
            if char.isdigit():
                department = course_code[:i]
                number = course_code[i:]
                break
            
    cursor.execute("SELECT ID FROM Courses WHERE Department = ? AND Code = ?", (department, number))
    result = cursor.fetchone()
    return result[0] if result else None

def get_courseID_by_title(cursor: sqlite3.Cursor, course_title: str) -> str:
    """Return the database course ID for a given course title.

    Args:
        sqlite3.Cursor cursor: cursor object connected to the registration database.
        str course_title: Course title to look up.
            Format: Exact course title as stored in the `Courses.Name` column (eg. "Introduction to Computer Science").

    Returns:
        str: The matching course ID.
            Format if found: Primary key value from `Courses.ID` column corresponding to the provided course title. (eg. "12345")
            Note: If no course is found with that title, returns ``None``.
    
    Warnings: This is designed for a database with unique course titles (with the exception of "Cooperative Work Experience"). If you plan to use this for a database that may have multiple courses with the same title, consider implementing an alternative lookup method.
    """
    cursor.execute("SELECT ID FROM Courses WHERE Name = ?", (course_title,))
    result = cursor.fetchone()
    return result[0] if result else None

def get_coops(cursor: sqlite3.Cursor) -> list:
    """Return a list of course IDs for all 'Cooperative Work Experience' entries.

    Args:
        sqlite3.Cursor cursor: cursor object connected to the registration database.

    Returns:
        list[str]: List of course IDs (from `Courses.ID`) for all courses with the name "Cooperative Work Experience".
            Format of list items: Primary key values from `Courses.ID` column corresponding to rows where `Courses.Name` is "Cooperative Work Experience" (eg. ["12345", "67890"]).
            Note: If no courses are found with that name, returns an empty list.
    """
    cursor.execute("SELECT ID, Department, Code FROM Courses WHERE Name = 'Cooperative Work Experience'")
    results = cursor.fetchall()
    return [row[0] for row in results]

def get_courseIDs_by_filters(cursor: sqlite3.Cursor, filters: schemas.CourseFilters) -> list:
    """Return a list of course IDs that match the provided CourseFilters.

    Builds a parameterized SQL query from the structured `schemas.CourseFilters` and returns matching `CoursesOffered.ID` values.

    Args:
        sqlite3.Cursor cursor: cursor object connected to the registration database.
        schemas.CourseFilters filters: Filters to apply to the course search.
            Format: {
                Optional[List[DBTerm]] terms,
                    DBTerm format: {
                        "year": int,
                            Format: 4-digit year (e.g. 2024)
                        "season": str,
                            Format: ["Fall", "Winter", "Spring", "Summer"]
                        "number": Optional[int]
                            Format: Integer term number (e.g. 1, 2, 3, etc). This is optional within each term filter; if not provided, the filter will match any term with the specified year and season regardless of term number.
                            Note: Exists to account for schools using a quarter system with multiple terms per season.
                    }
                    Note: Uses OR logic (can match any of the specified terms).
                Optional[List[str]] departments,
                    Format: List of department abbreviations as stored in `Courses.Department` (e.g. ["PHY", "MAT"]).
                    Note: Uses OR logic (can match any of the specified departments).
                Optional[List[CodeCondition]] course_codes,
                    CodeCondition format: {
                        "condition": str ["=" | ">" | "<" | ">=" | "<=" | "!="],
                        "code": str
                            Format: Course number as stored in `Courses.Code` (e.g. "101", "210", etc).
                    }
                    Note: Uses AND logic (must match all specified course code conditions).
                Optional[List[CreditCondition]] credits,
                    CreditCondition format: {
                        "condition": str ["=" | ">" | "<" | ">=" | "<=" | "!="],
                        "credits": int (e.g. 3 or 4)
                    }
                    Note: Uses AND logic (must match all specified credit conditions).
                Optional[List[str]] keywords,
                    Format: List of keywords to search for in the `Courses.Description` field.
                    Note: Uses OR logic (matches if any of the specified keywords are found in the description).
                Optional[List[str]] prerequisites,
                    Format: List of keywords to search for in the `Courses.Requirements` field.
                    Note: Uses OR logic (matches if any of the specified keywords are found in the requirements).
            }

    Returns:
        list[str]: List of matching course IDs.
            Format of list items: Primary key values from `CoursesOffered.ID` column corresponding to courses that match the provided filters (e.g. ["12345", "67890"]).
            Note: If `filters` is ``None``, returns a single-element list with the string "No filters specified". If no courses match the provided filters, returns an empty list.
        
    Raises:
        ValueError: If an invalid comparison operator is provided in course code or credit-related filters.
            Course code error message: "Invalid course code condition: {condition}"
            Credit error message: "Invalid credit condition: {condition}"
    """
    if filters is None:
        return ["No filters specified"]

    query = "SELECT co.ID FROM CoursesOffered as co JOIN Courses as c ON co.CourseID = c.ID"
    params = []

    # If a term filter is specified, add a JOIN to the Sections table and conditions to the query to filter by the specified terms
    if "terms" in filters.__dict__ and filters.terms is not None and len(filters.terms) > 0:
        query += " JOIN terms as t ON co.ParentID = t.ID WHERE 1=1"
        term_conditions = []
        for term in filters.terms:
            term_condition = "(t.Year = ? AND t.Season = ?"
            params.extend([term.year, term.season])
            if "number" in term.__dict__ and term.number is not None:
                term_condition += " AND t.Number = ?"
                params.append(term.number)
            term_condition += ")"
            term_conditions.append(term_condition)
        query += " AND (" + " OR ".join(term_conditions) + ")"
    else:
        query += " WHERE 1=1"

    # If a department filter is specified, add a condition to the query to filter by department
    if "departments" in filters.__dict__ and filters.departments is not None and len(filters.departments) > 0:
        query += " AND c.Department IN ({})".format(",".join("?" for _ in filters.departments))
        params.extend(filters.departments)

    if "course_codes" in filters.__dict__ and filters.course_codes is not None and len(filters.course_codes) > 0:
        query += " AND ("
        for course_code_condition in filters.course_codes:
            condition = course_code_condition.condition
            code = course_code_condition.code
            if condition not in ["=", ">", "<", ">=", "<=", "!="]:
                raise ValueError(f"Invalid course code condition: {condition}")
            query += f"c.Code {condition} ?"
            params.append(code)
            if course_code_condition != filters.course_codes[-1]:
                query += " AND "
        query += ")"

    # If a credit filter is specified, add a condition to the query to filter by number of credits
    if "credits" in filters.__dict__ and filters.credits is not None and len(filters.credits) > 0:
        query += " AND ("
        for credit_condition in filters.credits:
            condition = credit_condition.condition
            if condition not in ["=", ">", "<", ">=", "<=", "!="]:
                raise ValueError(f"Invalid credit condition: {condition}")
            credits = credit_condition.credits
            query += f"c.Credits {condition} ?"
            params.append(credits)
            if credit_condition != filters.credits[-1]:
                query += " AND "
        query += ")"

    if "keywords" in filters.__dict__ and filters.keywords is not None and len(filters.keywords) > 0:
        query += " AND ("
        for keyword in filters.keywords:
            query += "c.Description LIKE ?"
            params.extend([f"%{keyword}%"])
            if keyword != filters.keywords[-1]:
                query += " OR "
        query += ")"
    
    if "prerequisites" in filters.__dict__ and filters.prerequisites is not None and len(filters.prerequisites) > 0:
        query += " AND ("
        for prereq in filters.prerequisites:
            query += "c.Requirements LIKE ?"
            params.extend([f"%{prereq}%"])
            code = get_courseID_by_title(cursor, prereq)
            if code is not None:
                query += " OR c.Requirements LIKE ?"
                params.append(f"%{code}%")
            if prereq != filters.prerequisites[-1]:
                query += " OR "
        query += ")"

    # Execute the query with the specified conditions and return the IDs of the matching courses as a list
    cursor.execute(query, tuple(params))
    results = cursor.fetchall()
    return [row[0] for row in results]

def get_course_info_by_id(cursor: sqlite3.Cursor, course_id: str) -> dict:
    """Return course metadata for a given course ID.

    Args:
        sqlite3.Cursor cursor: cursor object connected to the registration database.
        str course_id: The ID of the course to retrieve.
            format: Primary key value from `Courses.ID` column (eg. "12345").

    Returns:
        dict: Mapping of column names to values for the matched course.
            Format: {
                "ID": str,
                    Format: Primary key value from `Courses.ID` column (eg. "12345")
                "Name": str,
                    Format: Course name as stored in `Courses.Name` (e.g. "Introduction to Computer Science")
                "Department": str,
                    Format: Department abbreviation as stored in `Courses.Department` (e.g. "HST")
                "Code": str,
                    Format: Course number as stored in `Courses.Code` (e.g. "101")
                "Credits": int,
                    Format: Number of credits as stored in `Courses.Credits` (e.g. 3)
                "Requirements": str
                    Format: Text string from `Courses.Requirements` column describing the course prerequisites and requirements (e.g. "Prerequisites: A in MAT 125 or appropriate placement score")
            }
            Note: If no course is found with that ID, returns an empty dict.
    """
    cursor.execute("SELECT ID, Name, Department, Code, Credits, Requirements FROM Courses WHERE ID = ?", (course_id,))
    row = cursor.fetchone()
    if row is None:
        return {}

    course_info = {}
    for idx, col in enumerate(cursor.description):
        course_info[col[0]] = row[idx]
    
    return course_info

def get_course_description_by_id(cursor: sqlite3.Cursor, course_id: str) -> str:
    """Return the textual description for a course identified by `course_id`.

    Args:
        sqlite3.Cursor cursor: cursor object connected to the registration database.
        str course_id: The ID of the course to retrieve the description for.
            Format: Primary key value from `Courses.ID` column (eg. "12345").

    Returns:
        str: Course description as stored in the `Courses.Description` column for the matched course (e.g. "An introduction to the fundamental concepts of computer science, including algorithms, data structures, software design, and basic programming skills.").
            Note: If no course is found with that ID, returns "Course not found".
    """
    cursor.execute("SELECT Description FROM Courses WHERE ID = ?", (course_id,))
    row = cursor.fetchone()
    if row is None:
        return "Course not found"
    return row[0]

def get_sectionIDs_by_filters(cursor: sqlite3.Cursor, filters: schemas.SectionFilters) -> list:
    """Return a list of section IDs that match the provided SectionFilters.

    Builds a parameterized SQL query from the structured `schemas.SectionFilters` and returns matching `Sections.ID` values.

    Args:
        sqlite3.Cursor cursor: cursor object connected to the registration database.
        schemas.SectionFilters filters: Filters to apply to the section search.
            Format: {
                Optional[List[DBTerm]] terms,
                    DBTerm format: {
                        "year": int,
                            Format: 4-digit year (e.g. 2024)
                        "season": str,
                            Format: ["Fall", "Winter", "Spring", "Summer"]
                        "number": Optional[int]
                            Format: Integer term number (e.g. 1, 2, 3, etc). This is optional within each term filter; if not provided, the filter will match any term with the specified year and season regardless of term number.
                            Note: Exists to account for schools using a quarter system with multiple terms per season.
                    }
                    Note: Uses OR logic (can match any of the specified terms).
                Optional[List[str]] course_codes,
                    Format: Course codes in either spaced or compact format (e.g. ["CSC 101", "MAT125"]).
                    Note: Uses OR logic (can match any of the specified course codes).
                Optional[List[str]] instructors,
                    Format: List of instructor names as stored in `Sections.Instructor` (e.g. ["Smith, John"]).
                    Note: Uses OR logic (can match any of the specified instructors).
                Optional[List[str]] teaching_methods,
                    Format: List of methods as stored in `Sections.Method` (e.g. ["In-Person", "Online"]).
                    Note: Uses OR logic (can match any of the specified methods).
                Optional[List[EnrollmentCondition]] enrollment_capacity,
                    EnrollmentCondition format: {
                        "condition": str ["=" | ">" | "<" | ">=" | "<=" | "!="],
                        "enrollment": int
                            Format: Integer seat count compared against `Sections.MaxSeats`.
                    }
                    Note: Uses AND logic (must match all specified enrollment capacity conditions).
                Optional[List[EnrollmentCondition]] enrollment,
                    EnrollmentCondition format: {
                        "condition": str ["=" | ">" | "<" | ">=" | "<=" | "!="],
                        "enrollment": int
                            Format: Integer seat count compared against `Sections.SeatsLeft`.
                    }
                    Note: Uses AND logic (must match all specified current enrollment conditions).
                Optional[List[str]] locations,
                    Format: List of location strings as stored in `Sections.Location` (e.g. ["MAIN Campus, Surprenant Hall, Computer Classroom, 123"]).
                    Note: Uses OR logic (can match any of the specified locations).
                Optional[List[DBMeetTime]] meet_times,
                    DBMeetTime format: {
                        "days": str,
                            Format: Day of the week as stored in `MeetTimes.Day` ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"].
                        "start_time": str,
                            Format: Time string as stored in `MeetTimes.StartTime` (e.g. "10:00").
                            Note: Uses 24-hour time format.
                        "end_time": str,
                            Format: Time string as stored in `MeetTimes.EndTime` (e.g. "10:50").
                            Note: Uses 24-hour time format.
                    }
                    Note: Uses OR logic (can match any of the specified meet time blocks).
            }

    Returns:
        list[str]: List of matching section IDs.
            Format of list items: Primary key values from `Sections.ID` column corresponding to sections that match the provided filters (e.g. ["12345", "67890"]).
            Note: If `filters` is ``None``, returns a single-element list with the string "No filters specified". If no sections match the provided filters, returns an empty list.
    
    Raises:
        ValueError: If an invalid comparison operator is provided in enrollment capacity or current enrollment filters.
            Enrollment capacity error message: "Invalid enrollment capacity condition: {condition}"
            Current enrollment error message: "Invalid enrollment condition: {condition}"
    """
    if filters is None:
        return ["No filters specified"]
    
    query = "SELECT s.ID FROM Sections as s"
    params = []

    # If a course code and/or term filter is specified, add a JOIN to the Courses table
    if "course_codes" in filters.__dict__ and filters.course_codes is not None and len(filters.course_codes) > 0 or "terms" in filters.__dict__ and filters.terms is not None and len(filters.terms) > 0:
        query += " JOIN CoursesOffered as co ON s.ParentID = co.ID JOIN Courses as c ON co.CourseID = c.ID"

    # If a meet time filter is specified, add a JOIN to the MeetTimes table
    if "meet_times" in filters.__dict__ and filters.meet_times is not None and len(filters.meet_times) > 0:
        query += " JOIN MeetTimes as mt ON s.ID = mt.ParentID"

    # If a term filter is specified, add a JOIN to the Terms table and conditions to the query to filter by the specified terms
    if "terms" in filters.__dict__ and filters.terms is not None and len(filters.terms) > 0:
        query += " JOIN Terms as t ON co.ParentID = t.ID WHERE 1=1"
        term_conditions = []
        for term in filters.terms:
            term_condition = "(t.Year = ? AND t.Season = ?"
            params.extend([term.year, term.season])
            if "number" in term.__dict__ and term.number is not None:
                term_condition += " AND t.Number = ?"
                params.append(term.number)
            term_condition += ")"
            term_conditions.append(term_condition)
        query += " AND (" + " OR ".join(term_conditions) + ")"
    else:
        query += " WHERE 1=1"
    
    # If a course code filter is specified, add conditions to the query to filter by the specified course codes
    if "course_codes" in filters.__dict__ and filters.course_codes is not None and len(filters.course_codes) > 0:
        course_code_conditions = []
        for course_code in filters.course_codes:
            # check if which format the course code is in (e.g. "CSC 101" vs "CSC101") and split accordingly
            if " " in course_code:
                # split by space
                department, number = course_code.split()
            else:                
                # split by the point where the digits start
                for i, char in enumerate(course_code):
                    if char.isdigit():
                        department = course_code[:i]
                        number = course_code[i:]
                        break
            course_code_conditions.append("(c.Department = ? AND c.Code = ?)")
            params.extend([department, number])
        query += " AND (" + " OR ".join(course_code_conditions) + ")"
    
    # If an instructor filter is specified, add conditions to the query to filter by the specified instructors
    if "instructors" in filters.__dict__ and filters.instructors is not None and len(filters.instructors) > 0:
        instructor_conditions = []
        for instructor in filters.instructors:
            instructor_conditions.append("(s.Instructor = ?)")
            params.append(instructor)
        query += " AND (" + " OR ".join(instructor_conditions) + ")"
    
    # If a teaching method filter is specified, add conditions to the query to filter by the specified teaching methods
    if "teaching_methods" in filters.__dict__ and filters.teaching_methods is not None and len(filters.teaching_methods) > 0:
        teaching_method_conditions = []
        for method in filters.teaching_methods:
            teaching_method_conditions.append("(s.Method = ?)")
            params.append(method)
        query += " AND (" + " OR ".join(teaching_method_conditions) + ")"

    # If an enrollment capacity filter is specified, add a condition to the query to filter by enrollment capacity
    if "enrollment_capacity" in filters.__dict__ and filters.enrollment_capacity is not None and len(filters.enrollment_capacity) > 0:
        query += " AND ("
        for enrollment_condition in filters.enrollment_capacity:
            condition = enrollment_condition.condition
            if condition not in ["=", ">", "<", ">=", "<=", "!="]:
                raise ValueError(f"Invalid enrollment capacity condition: {condition}")
            query += f"s.MaxSeats {condition} ?"
            params.append(enrollment_condition.enrollment)
            if enrollment_condition != filters.enrollment_capacity[-1]:
                query += " AND "
        query += ")"

    # If a current enrollment filter is specified, add a condition to the query to filter by current enrollment
    if "enrollment" in filters.__dict__ and filters.enrollment is not None and len(filters.enrollment) > 0:
        query += " AND ("
        for enrollment_condition in filters.enrollment:
            condition = enrollment_condition.condition
            if condition not in ["=", ">", "<", ">=", "<=", "!="]:
                raise ValueError(f"Invalid enrollment condition: {condition}")
            query += f"s.SeatsLeft {condition} ?"
            params.append(enrollment_condition.enrollment)
            if enrollment_condition != filters.enrollment[-1]:
                query += " AND "
        query += ")"

    # If a location filter is specified, add conditions to the query to filter by the specified locations
    if "locations" in filters.__dict__ and filters.locations is not None and len(filters.locations) > 0:
        location_conditions = []
        for location in filters.locations:
            location_conditions.append("(s.Location = ?)")
            params.append(location)
        query += " AND (" + " OR ".join(location_conditions) + ")"
    
    # If a meet time filter is specified, add conditions to the query to filter by the specified meet times
    if "meet_times" in filters.__dict__ and filters.meet_times is not None and len(filters.meet_times) > 0:
        meet_time_conditions = []
        for meet_time in filters.meet_times:
            meet_time_condition = "(mt.Day = ? AND mt.StartTime = ? AND mt.EndTime = ?)"
            params.extend([meet_time.days, meet_time.start_time, meet_time.end_time])
            meet_time_conditions.append(meet_time_condition)
        query += " AND (" + " OR ".join(meet_time_conditions) + ")"

    # Execute the query with the specified conditions and return the IDs of the matching sections as a list
    cursor.execute(query, tuple(params))
    results = cursor.fetchall()
    return [row[0] for row in results]

def get_section_info_by_id(cursor: sqlite3.Cursor, section_id: str) -> dict:
    """Return section-level metadata for the provided section ID.

    Returns combined data from `Sections`, its parent `CoursesOffered`, and the
    underlying `Courses` row (department, code, course name, instructor, method,
    location, capacity and seats left).

    Args:
        sqlite3.Cursor cursor: cursor object connected to the registration database.
        str section_id: The ID of the section to retrieve.
            Format: Primary key value from `Sections.ID` column (eg. "12345").

    Returns:
        dict: Mapping of column names to values for the matched section.
            Format: {
                "ID": str,
                    Format: Primary key value from `Sections.ID` column (eg. "12345")
                "Department": str,
                    Format: Department abbreviation as stored in `Courses.Department` (e.g. "HST")
                "Code": str,
                    Format: Course number as stored in `Courses.Code` (e.g. "101")
                "Name": str,
                    Format: Course name as stored in `Courses.Name` (e.g. "Introduction to Computer Science")
                "SectionNum": str,
                    Format: Section number as stored in `Sections.SectionNum` (e.g. "001", "002A", etc)
                "Instructor": str,
                    Format: Instructor name(s) as stored in `Sections.Instructor` (e.g. "Smith, John")
                "Method": str,
                    Format: Teaching method as stored in `Sections.Method` (e.g. "In-Person", "Online", etc)
                "Location": str,
                    Format: Location string as stored in `Sections.Location` (e.g. "MAIN Campus, Surprenant Hall, Computer Classroom, 123")
                "MaxSeats": int,
                    Format: Maximum enrollment capacity as stored in `Sections.MaxSeats` (e.g. 30)
                "SeatsLeft": int
                    Format: Number of seats left as stored in `Sections.SeatsLeft` (e.g. 5)
            }
            Note: If no section is found with that ID, returns an empty dict.
    """
    cursor.execute("SELECT s.ID, c.Department, c.Code, c.Name, s.SectionNum, s.Instructor, s.Method, s.Location, s.MaxSeats, s.SeatsLeft FROM Sections as s JOIN CoursesOffered as co ON s.ParentID = co.ID JOIN Courses as c ON co.CourseID = c.ID WHERE s.ID = ?", (section_id,))
    row = cursor.fetchone()
    if row is None:
        return {}

    section_info = {}
    for idx, col in enumerate(cursor.description):
        section_info[col[0]] = row[idx]
    
    return section_info

def get_upcoming_events(cursor: sqlite3.Cursor):
    """Return a list of upcoming events that have at least one future EventDates row.

    Args:
        sqlite3.Cursor cursor: cursor object connected to the registration database.

    Returns:
        list[dict]: List of dicts each containing "ID", "Name", and "Description" for upcoming events.
            Format of list items: {
                "ID": str,
                    Format: Primary key value from `Events.ID` column (eg. "12345")
                "Name": str,
                    Format: Event name as stored in `Events.Name` (e.g. "Spring Career Fair")
                "Description": str
                    Format: Text string from `Events.Description` column describing the event (e.g. "An annual career fair held each spring featuring employers from various industries recruiting for internships and full-time positions.")
            }
    """
    cursor.execute("SELECT e.ID, e.Name, e.Description FROM Events as e JOIN EventDates as ed ON e.ID = ed.ParentID WHERE ed.Date >= date('now') GROUP BY e.ID")
    events = []
    for row in cursor.fetchall():
        events.append({
            "ID": row[0],
            "Name": row[1],
            "Description": row[2]
        })
    return events

def get_event_dates_by_name(cursor: sqlite3.Cursor, event_name: str) -> list:
    """Return all future EventDates for an event identified by its name.

    Args:
        sqlite3.Cursor cursor: cursor object connected to the registration database.
        str event_name: The name of the event to retrieve dates for.
            Format: Exact event name as stored in `Events.Name` column (e.g. "Spring Career Fair").

    Returns:
        list[dict]: List of dicts each containing "Date", "StartTime", "EndTime", and "Location" for future dates of the specified event.
            Format of list items: {
                "Date": str,
                    Format: Date string as stored in `EventDates.Date` column (e.g. "2026-03-15")
                "StartTime": str,
                    Format: Time string as stored in `EventDates.StartTime` column (e.g. "10:00")
                    Note: Uses 24-hour time format.
                "EndTime": str,
                    Format: Time string as stored in `EventDates.EndTime` column (e.g. "14:00")
                    Note: Uses 24-hour time format.
                "Location": str
                    Format: Location string as stored in `EventDates.Location` column describing where the event will take place (e.g. "Main Campus, Herrington Learning Center, Room 109A")
            }
            Note: If no event is found with the provided name, returns ["Event not found"]. If the event is found but has no future dates, returns an empty list.
    """
    cursor.execute("SELECT ID FROM Events WHERE Name = ?", (event_name,))
    result = cursor.fetchone()

    if result is None:
        return ["Event not found"]

    cursor.execute("SELECT Date, StartTime, EndTime, Location FROM EventDates WHERE ParentID = ? AND Date >= date('now')", (result[0],))
    event_dates = []
    for row in cursor.fetchall():
        event_dates.append({
            "Date": row[0],
            "StartTime": row[1],
            "EndTime": row[2],
            "Location": row[3]
        })

    return event_dates

def get_student_basic_info(cursor: sqlite3.Cursor, student_id: int) -> dict:
    """Return basic profile information for a student.

    Args:
        sqlite3.Cursor cursor: cursor object connected to the registration database.
        int student_id: The numeric ID of the student to retrieve information for.
            Format: Primary key value from `Students.ID` column (e.g. 12345).

    Returns:
        dict: Mapping of profile information fields to their corresponding values for the specified student.
            Format: {
                "Name": str,
                    Format: Student's name as stored in `Students.Name` column (e.g. "Alice Johnson")
                "Advisor": str,
                    Format: Student's advisor name as stored in `Students.AdvisorID` column (e.g. "Dr. Smith").
                    Note: If no advisor is assigned, returns "No advisor assigned".
                "GPA": float,
                    Format: Student's GPA as stored in `Students.GPA` column (e.g. 3.75)
                "CreditsEarned": int,
                    Format: Total number of credits earned by the student as stored in `Students.CreditsEarned` column (e.g. 56)
                "ProgramsOfStudy": list[dict],
                    Format: List of dicts each containing program information for the student's programs of study.
                        Format of list items: {
                            "Title": str,
                                Format: Program title as stored in `ProgramsOfStudy.Title` column (e.g. "Computer Information Systems")
                            "Description": str,
                                Format: Text string from `ProgramsOfStudy.Description` column describing the program (e.g. "A program focused on the application of computing technology in business settings, covering topics such as information systems analysis, database management, and IT project management.")
                            "CreditsRequired": int
                                Format: Total number of credits required to complete the program as stored in `ProgramsOfStudy.CreditsRequired` column (e.g. 60)
                        }
                    Note: If the student is not enrolled in any programs of study, returns ["No program of study"].
            }
            Note: If no student is found with that ID, returns an empty dict.
    """
    cursor.execute("SELECT Name, AdvisorID, GPA, CreditsEarned FROM Students WHERE ID = ?", (student_id,))
    row = cursor.fetchone()

    if row is None:
        return {}

    name = row[0]
    advisor = row[1]
    gpa = row[2]
    credits_earned = row[3]

    cursor.execute("SELECT p.Title, p.Description, p.CreditsRequired FROM ProgramsOfStudy as p JOIN StudentPrograms as sp ON p.ID = sp.ProgramID WHERE sp.ParentID = ?", (student_id,))
    programs_of_study = []
    for row in cursor.fetchall():
        programs_of_study.append({
            "Title": row[0],
            "Description": row[1],
            "CreditsRequired": row[2]
        })

    if not advisor:
        advisor = "No advisor assigned"

    if not programs_of_study:
        programs_of_study = ["No program of study"]
    
    student_info = {
        "Name": name,
        "Advisor": advisor,
        "GPA": gpa,
        "CreditsEarned": credits_earned,
        "ProgramsOfStudy": programs_of_study
    }

    return student_info

def get_student_course_history(cursor: sqlite3.Cursor, student_id: int) -> list:
    """Return a student's course history as a list of course entries.

    Args:
        sqlite3.Cursor cursor: cursor object connected to the registration database.
        int student_id: The numeric ID of the student to retrieve course history for.
            Format: Primary key value from `Students.ID` column (e.g. 12345).

    Returns:
        list[dict]: List of dicts each containing "CourseCode", "Name", and "Grade" for courses the student has taken.
            Format of list items: {
                "CourseCode": str,
                    Format: Concatenation of department and course code as stored in `Courses.Department` and `Courses.Code` (e.g. "PHI 101")
                "Name": str,
                    Format: Course name as stored in `Courses.Name` (e.g. "Introduction to Philosophy")
                "Grade": str
                    Format: Grade received for the course as stored in `CoursesTaken.Grade` column ["A" | "A-" | "B+" | "B" | "B-" | "C+" | "C" | "C-" | "D+" | "D" | "D-" | "F" | "IP" | "W", "NR"]
            }
            Note: If the student has not taken any courses, returns ["No courses taken"].
    """
    cursor.execute("SELECT c.Department, c.Code, c.Name, ct.Grade FROM Courses as c JOIN CoursesTaken as ct ON c.ID = ct.CourseID WHERE ct.ParentID = ?", (student_id,))
    course_history = []
    for row in cursor.fetchall():
        course_history.append({
            "CourseCode": str(row[0]) + " " + str(row[1]),
            "Name": row[2],
            "Grade": row[3]
        })
    if not course_history:
        course_history = ["No courses taken"]
    return course_history

def get_student_interests(cursor: sqlite3.Cursor, student_id: int) -> list:
    """Return a list of interests for the given student.

    Args:
        sqlite3.Cursor cursor: cursor object connected to the registration database.
        int student_id: The numeric ID of the student to retrieve interests for.
            Format: Primary key value from `Students.ID` column (e.g. 12345).

    Returns:
        list[str]: List of interests as stored in the `Interests` table for the specified student.
            Format of list items: Interest string as stored in `Interests.Interest` column (e.g. "Artificial Intelligence"). 
            Note: If the student has not specified any interests, returns ["No interests specified"].
    """
    cursor.execute("SELECT Interest FROM Interests WHERE ParentID = ?", (student_id,))
    interests = [row[0] for row in cursor.fetchall()]
    if not interests:
        interests = ["No interests specified"]
    return interests

def get_student_tracked_sections(cursor: sqlite3.Cursor, student_id: int) -> list:
    """Return the list of sections a student is currently tracking.

    Args:
        sqlite3.Cursor cursor: cursor object connected to the registration database.
        int student_id: The numeric ID of the student to retrieve tracked sections for.
            Format: Primary key value from `Students.ID` column (e.g. 12345).

    Returns:
        list[dict]: List of tracked sections.
            Format of list items: {
                "CourseCode": str,
                    Format: Concatenation of department and course code as stored in `Courses.Department` and `Courses.Code` (e.g. "CHM 102")
                "SectionNumber": str,
                    Format: Section number as stored in `Sections.SectionNum` (e.g. "1", "b1", "50", etc)
                "Name": str
                    Format: Course name as stored in `Courses.Name` (e.g. "General Chemistry II")
            }
            Note: If the student is not tracking any sections, returns ["No sections currently being tracked"]. 
    """
    cursor.execute("SELECT c.Department, c.Code, c.Name, s.SectionNum FROM Courses as c JOIN Sections as s JOIN CoursesOffered as co JOIN TrackedSections as ts ON c.ID = co.CourseID AND s.ParentID = co.ID AND s.ID = ts.SectionID WHERE ts.ParentID = ?", (student_id,))
    tracked_sections = []
    for row in cursor.fetchall():
        tracked_sections.append({
            "CourseCode": str(row[0]) + " " + str(row[1]),
            "SectionNumber": str(row[3]),
            "Name": str(row[2])
        })
    if not tracked_sections:
        tracked_sections = ["No sections currently being tracked"]
    return tracked_sections

def get_program_requirements_by_title(cursor: sqlite3.Cursor, program_title: str) -> list:
    """Return program requirement strings for a program identified by its Title.

    Args:
        sqlite3.Cursor cursor: cursor object connected to the registration database.
        str program_title: The title of the program to retrieve requirements for.
            Format: Exact program title as stored in `ProgramsOfStudy.Title` column (e.g. "Computer Information Systems").

    Returns:
        list[str]: List of requirement strings for the specified program.
            Format of list items: Text string describing a program requirement, which may include specific course options and/or elective options.
                Format for course options: "Department: {Department}, Course Number: {Code}, Title: {Name}"
                Format for elective options: "Any {Elective} course"
                Note: If a requirement includes multiple options of how to fulfill it, the options will be separated by " OR " in the string.
            Note: If no program is found with the provided title, returns ["Program not found"]. If the program is found but has no requirements, returns ["No requirements found"].
    """
    cursor.execute("""SELECT prc.ID FROM ProgramRequiredCourses as prc JOIN ProgramsOfStudy as p ON prc.ParentID = p.ID WHERE p.Title = ?""", (program_title,))
    if cursor.fetchone() is None:
        return ["Program not found"]
    program_requirements = []
    for row in cursor.fetchall():
        c_options = cursor.execute("""SELECT c.Department, c.Code, c.Name FROM Courses as c JOIN ProgramRequiredCourseOptions as prco Join ProgramRequiredCourses as prc ON c.ID = prco.CourseID AND prc.ID = prco.ParentID WHERE prc.ID = ? AND prco.CourseID IS NOT NULL""", (row[0],)).fetchall()
        d_options = cursor.execute("""SELECT Elective FROM ProgramRequiredCourseOptions as prco Join ProgramRequiredCourses as prc ON prco.ParentID = prc.ID WHERE prc.ID = ? AND prco.CourseID IS NULL""", (row[0],)).fetchall()
        requirement = ""
        for option in c_options:

            requirement += "Department: " + str(option[0]) + ", Course Number: " + str(option[1]) + ", Title: " + str(option[2])
            if option != c_options[-1] or len(d_options) > 0:
                requirement += " OR "
        for option in d_options:
            requirement += "Any " + str(option[0]) + " course"
            if option != d_options[-1]:
                requirement += " OR "
        program_requirements.append(requirement)
    
    if not program_requirements:
        program_requirements = ["No requirements found"]
    return program_requirements

def insert_student_interests(conn: sqlite3.Connection, student_id: int, interest: list[str]) -> str:
    """Insert one or more interest strings for a student.

    Args:
        sqlite3.Connection conn: Connection object connected to the registration database.
        int student_id: The student's numeric ID.
            Format: Primary key value from `Students.ID` column (e.g. 12345).
        list[str] interest: List of interest strings to be inserted.
            Format of list items: Interest string to be stored in `Interests.Interest` column (e.g. "Data Science", "Machine Learning", "Cybersecurity", etc).

    Returns:
        str: Confirmation string indicating how many interests were added.
            Format: "{counter} new interest(s) added"
    """
    counter = 0
    cursor = conn.cursor()
    for item in interest:
        cursor.execute("INSERT INTO Interests (ParentID, Interest) VALUES (?, ?)", (student_id, item))
        counter += 1
    conn.commit()

    return f"{counter} new interest(s) added"

def insert_student_tracked_section(conn: sqlite3.Connection, student_id: int, course_code: str, section_number: str) -> str:
    """Add a tracked section for the student specified.

    Args:
        sqlite3.Connection conn: Connection object connected to the registration database.
        int student_id: The student's numeric ID.
            Format: Primary key value from `Students.ID` column (e.g. 12345).
        str course_code: The course code of the section to be tracked.
            Format: Course code in either spaced or compact format (e.g. "CSC 101" or "CSC101").
        str section_number: The section number of the section to be tracked.
            Format: Section number as stored in `Sections.SectionNum` (e.g. "1", "b1", "50", etc).

    Returns:
        str: Confirmation string indicating the result of the operation.
            Possible return values:
                "Section added to tracked sections" - if the section was successfully added to the student's tracked sections.
                "Section not found" - if no section matches the provided course code and section number.
                "Section already being tracked" - if the student is already tracking a section with the same course code and section number.
    """
    # get section ID based on course code and section number
    if " " in course_code:
        # split by space
        department, number = course_code.split()
    else:
        # split by the point where the digits start
        for i, char in enumerate(course_code):
            if char.isdigit():
                department = course_code[:i]
                number = course_code[i:]
                break
    cursor = conn.cursor()
    cursor.execute("SELECT s.ID FROM Sections as s JOIN CoursesOffered as co JOIN Courses as c ON s.ParentID = co.ID AND co.CourseID = c.ID WHERE c.Department = ? AND c.Code = ? AND s.SectionNum = ?", (department, number, section_number))
    result = cursor.fetchone()

    if result is None:
        return "Section not found"
    
    section_id = result[0]
    # check if the section is already being tracked by the student to avoid duplicates
    cursor.execute("SELECT ID FROM TrackedSections WHERE ParentID = ? AND SectionID = ?", (student_id, section_id))
    if cursor.fetchone() is not None:
        return "Section already being tracked"
    cursor.execute("INSERT INTO TrackedSections (ParentID, SectionID) VALUES (?, ?)", (student_id, section_id))
    conn.commit()
    return "Section added to tracked sections"

def get_data_with_hierarchy(cursor: sqlite3.Cursor, table: str, targetID: int) -> dict:
    """Recursively gather an entry and all related rows that reference it.

    Starting from the provided table and targetID, this function fetches the row's
    non-ID fields and then discovers tables that declare a FOREIGN KEY referencing
    the target table. For each related table, it recurses and includes that data
    under the parent entry.

    Args:
        sqlite3.Cursor cursor: cursor object connected to the registration database.
        str table: The name of the table to start from (e.g. "Courses", "Students", etc).
        int targetID: The ID of the row in the specified table to retrieve (e.g. 12345).

    Returns:
        dict: A nested dictionary representing the target entry and all related entries that reference it, structured to indicate the relationships between the data.
            Format: {
                "entry": str,
                    Format: A string combining the table name and target ID (e.g. "Courses: 12345").
                "content": dict,
                    Format: A dictionary containing the fields and values of the target entry, as well as nested dictionaries for any related entries that reference it.
                    The keys for the fields of the target entry are the column names from the table (excluding "ID" and "ParentID"), and the values are the corresponding field values from the database.
                    For each related table that references the target entry, there is a key in the content dict with the name of that related table, and its value is a list of dicts representing each entry in that related table that references the target entry. Each of those dicts has the same structure as described here, allowing for recursive nesting to represent multiple levels of relationships.
            }

    Warnings:
        This can produce very large results for highly-referenced tables (catalogs).
    """
    results = {}
    entry = {}

    results["entry"] = table + ": " + str(targetID)

    # Get the entry from the target table that corresponds to the target and add its fields and values to the results
    for row in cursor.execute(f"SELECT * FROM {table} WHERE ID = ?", (targetID,)):
        for idx, col in enumerate(cursor.description):
            if col[0] != "ID" and col[0] != "ParentID" and row[idx] is not None:
                entry[col[0]] = row[idx]

    # Find all tables that reference target as a foreign key
    cursor.execute(
        '''
        SELECT name 
        FROM sqlite_master 
        WHERE type='table' AND sql LIKE ?
        ''', 
        (f'%REFERENCES {table}(ID)%',)
    )
    related_tables = [row[0] for row in cursor.fetchall()]

    # Loop through each related table and get all entries that reference the target entry, along with their relevant linked data based on the hierarchy, and add this information to the results in a structured format that indicates the relationships between the data
    if related_tables:
        for table in related_tables:
            entry[f"{table}"] = get_data_with_hierarchy(cursor, table, targetID)
    
    results["content"] = entry
    return results

def _format_hierarchy_node(node: dict, depth: int = 0) -> str:
    """Format a hierarchical node (from get_data_with_hierarchy) into a readable string.

    This helper is used by `hierarchy_data_to_string` to pretty-print the nested
    structure produced by `get_data_with_hierarchy`.

    Args:
        dict node: A dict representing a node in the hierarchy, with keys "entry" and "content".
        int depth: Current depth in the hierarchy, used for indentation.

    Returns:
        str: A formatted multi-line string representing the node and its children in a readable way.
    """
    indent = "  " * depth
    inner_indent = "  " * (depth + 1)
    lines = [f"{indent}{{"]
    lines.append(f"{inner_indent}\"entry\": \"{node['entry']}\",")

    content = node.get("content", {})
    field_items = []
    child_items = []

    for key, value in content.items():
        if isinstance(value, dict) and "entry" in value and "content" in value:
            child_items.append((key, value))
        else:
            field_items.append((key, value))

    lines.append(f"{inner_indent}\"fields\": {{")
    for idx, (key, value) in enumerate(field_items):
        comma = "," if idx < len(field_items) - 1 else ""
        value_str = str(value).replace('"', '\\"')
        lines.append(f"{inner_indent}  \"{key}\": \"{value_str}\"{comma}")
    lines.append(f"{inner_indent}}},")

    lines.append(f"{inner_indent}\"children\": {{")
    for idx, (key, child) in enumerate(child_items):
        child_block = _format_hierarchy_node(child, depth + 2)
        child_lines = child_block.split("\n")
        comma = "," if idx < len(child_items) - 1 else ""

        if child_lines:
            lines.append(f"{inner_indent}  \"{key}\": {child_lines[0].lstrip()}")
            for child_line in child_lines[1:-1]:
                lines.append(child_line)
            lines.append(f"{child_lines[-1]}{comma}")
    lines.append(f"{inner_indent}}}")

    lines.append(f"{indent}}}")
    return "\n".join(lines)

def hierarchy_data_to_string(hierarchy_data: dict) -> str:
    """Convert a hierarchy data dict into a readable multi-line string.

    Args:
        dict hierarchy_data: A dict representing hierarchical data as produced by `get_data_with_hierarchy`.

    Returns:
        str: A formatted multi-line string representing the hierarchy in a readable way.
    """
    return _format_hierarchy_node(hierarchy_data)

def get_data_with_hierarchy_string(cursor: sqlite3.Cursor, table: str, targetID: str) -> str:
    """Helper that returns the hierarchical data for a target as a formatted string.

    Args:
        sqlite3.Cursor cursor: cursor object connected to the registration database.
        str table: The name of the table to start from (e.g. "Courses", "Students", etc).
        int targetID: The ID of the row in the specified table to retrieve (e.g. 12345).

    Returns:
        str: A formatted multi-line string representing the target entry and all related entries that reference it, structured to indicate the relationships between the data.
            Format: {
                "entry": str,
                    Format: A string combining the table name and target ID (e.g. "Courses: 12345").
                "content": dict,
                    Format: A dictionary containing the fields and values of the target entry, as well as nested dictionaries for any related entries that reference it.
                    The keys for the fields of the target entry are the column names from the table (excluding "ID" and "ParentID"), and the values are the corresponding field values from the database.
                    For each related table that references the target entry, there is a key in the content dict with the name of that related table, and its value is a list of dicts representing each entry in that related table that references the target entry. Each of those dicts has the same structure as described here, allowing for recursive nesting to represent multiple levels of relationships.
                }
    
    Warnings:
        This can produce very large results for highly-referenced tables (catalogs).
    """
    hierarchy_data = get_data_with_hierarchy(cursor, table, targetID)
    return hierarchy_data_to_string(hierarchy_data)

def get_ids_by_field_value(cursor: sqlite3.Cursor, table: str, field: str, value: str) -> list:
    """Return a list of IDs in `table` where `field` equals `value`.

    Args:
        sqlite3.Cursor cursor: cursor object connected to the registration database.
        str table: The name of the table to query (e.g. "Courses", "Students", etc).
        str field: The name of the field/column to filter by (e.g. "Department", "AdvisorID", etc).
        str value: The value to match in the specified field (e.g. "CSC", "Dr. Smith", etc).

    Returns:
        list[str]: List of IDs (as strings) from the specified table where the specified field matches the provided value.
            Format of list items: Primary key values from the `ID` column of the specified table that match the condition (e.g. ["12345", "67890", etc]).
    """
    cursor.execute(f"SELECT ID FROM {table} WHERE {field} = ?", (value,))
    results = cursor.fetchall()
    return [row[0] for row in results]

def get_ids_by_parent(cursor: sqlite3.Cursor, table: str, targetID: str) -> list:
    """Return IDs from `table` whose `ParentID` equals `targetID`.

    Args:
        sqlite3.Cursor cursor: cursor object connected to the registration database.
        str table: The name of the table to query (e.g. "Courses", "Students", etc).
        str targetID: The value to match in the `ParentID` field (e.g. "12345", "67890", etc).

    Returns:
        list[str]: List of IDs (as strings) from the specified table where `ParentID` matches the provided targetID.
            Format of list items: Primary key values from the `ID` column of the specified table that match the condition (e.g. ["12345", "67890", etc]).
    """
    cursor.execute(f"SELECT ID FROM {table} WHERE ParentID = ?", (targetID,))
    results = cursor.fetchall()
    return [row[0] for row in results]

def get_students_by_advisor(cursor: sqlite3.Cursor, advisorID: str) -> list:
    """Return a list of student IDs advised by the given advisor.

    Args:
        sqlite3.Cursor cursor: cursor object connected to the registration database.
        str advisorID: Advisor identifier used in `Students.AdvisorID`.

    Returns:
        list[str]: List of student IDs (as strings) advised by the given advisor.
            Format of list items: Primary key values from the `ID` column of the `Students` table where `AdvisorID` matches the provided advisorID (e.g. ["12345", "67890", etc]).
    """
    cursor.execute("SELECT ID FROM Students WHERE AdvisorID = ?", (advisorID,))
    results = cursor.fetchall()
    return [row[0] for row in results]
