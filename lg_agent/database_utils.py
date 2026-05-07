import sys, os

# adds lg_agent directory to system path if not already there
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from lg_agent.utilities import schemas
import sqlite3

# Utility function to get course ID by course code
def get_courseID_by_code(cursor: sqlite3.Cursor, course_code: str) -> str:
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

# Utility function to get course ID by course title
def get_courseID_by_title(cursor: sqlite3.Cursor, course_title: str) -> str:
    cursor.execute("SELECT ID FROM Courses WHERE Name = ?", (course_title,))
    result = cursor.fetchone()
    return result[0] if result else None

def get_coops(cursor: sqlite3.Cursor) -> list:
    cursor.execute("SELECT ID, Department, Code FROM Courses WHERE Name = 'Cooperative Work Experience'")
    results = cursor.fetchall()
    return [row[0] for row in results]

# Utility function to filter courses based on certain criteria and return their IDs as a list
def get_courseIDs_by_filters(cursor: sqlite3.Cursor, filters: schemas.CourseFilters) -> list:
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
        if ")" in filters.departments:
            raise ValueError("Invalid department name: department names cannot contain parentheses (no sql injection allowed)")
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

# Utility function to get course info by course ID, including all requirements and prerequisites, and return this information as a dictionary
def get_course_info_by_id(cursor: sqlite3.Cursor, course_id: str) -> dict:
    cursor.execute("SELECT ID, Name, Department, Code, Credits, Requirements FROM Courses WHERE ID = ?", (course_id,))
    row = cursor.fetchone()
    if row is None:
        return {}

    course_info = {}
    for idx, col in enumerate(cursor.description):
        course_info[col[0]] = row[idx]
    
    return course_info

def get_course_description_by_id(cursor: sqlite3.Cursor, course_id: str) -> str:
    cursor.execute("SELECT Description FROM Courses WHERE ID = ?", (course_id,))
    row = cursor.fetchone()
    if row is None:
        return "Course not found"
    return row[0]

# Utility function to filter sections based on certain criteria and return their IDs as a list
def get_sectionIDs_by_filters(cursor: sqlite3.Cursor, filters: schemas.SectionFilters) -> list:
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
    cursor.execute("SELECT s.ID, c.Department, c.Code, c.Name, s.SectionNum, s.Instructor, s.Method, s.Location, s.MaxSeats, s.SeatsLeft FROM Sections as s JOIN CoursesOffered as co ON s.ParentID = co.ID JOIN Courses as c ON co.CourseID = c.ID WHERE s.ID = ?", (section_id,))
    row = cursor.fetchone()
    if row is None:
        return {}

    section_info = {}
    for idx, col in enumerate(cursor.description):
        section_info[col[0]] = row[idx]
    
    return section_info

# Utility function to get a list of events that have event dates that are in the future
def get_upcoming_events(cursor: sqlite3.Cursor):
    cursor.execute("SELECT e.ID, e.Name, e.Description FROM Events as e JOIN EventDates as ed ON e.ID = ed.ParentID WHERE ed.Date >= date('now') GROUP BY e.ID")
    events = []
    for row in cursor.fetchall():
        events.append({
            "ID": row[0],
            "Name": row[1],
            "Description": row[2]
        })
    return events

# Utility function to get all future event dates for a specific event based on its name
def get_event_dates_by_name(cursor: sqlite3.Cursor, event_name: str) -> list:
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

# Utility function to that returns the name, advisor, gpa, credits earned, and programs of study for a student based on their ID.
def get_student_basic_info(cursor: sqlite3.Cursor, student_id: int) -> dict:
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

# Utility function that returns the course code and course title for all courses a student has taken based on their ID
def get_student_course_history(cursor: sqlite3.Cursor, student_id: int) -> list:
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

# Utility function to get all interests for a student based on their ID
def get_student_interests(cursor: sqlite3.Cursor, student_id: int) -> list:
    cursor.execute("SELECT Interest FROM Interests WHERE ParentID = ?", (student_id,))
    interests = [row[0] for row in cursor.fetchall()]
    if not interests:
        interests = ["No interests specified"]
    return interests

# Utility function to get all tracked sections for a student based on their ID
def get_student_tracked_sections(cursor: sqlite3.Cursor, student_id: int) -> list:
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

# Utility function to get the courses required for a specific program of study based on its Title
def get_program_requirements_by_title(cursor: sqlite3.Cursor, program_title: str) -> list:
    cursor.execute("""SELECT prc.ID FROM ProgramRequiredCourses as prc JOIN ProgramsOfStudy as p ON prc.ParentID = p.ID WHERE p.Title = ?""", (program_title,))
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
    
    return program_requirements

# Utility function to insert new interests for a student based on their ID
def insert_student_interests(cursor: sqlite3.Cursor, student_id: int, interest: list[str]) -> str:
    counter = 0
    for item in interest:
        cursor.execute("INSERT INTO Interests (ParentID, Interest) VALUES (?, ?)", (student_id, item))
        counter += 1
    return f"{counter} new interest(s) added"

# Utility function to insert a new tracked section for a student based on their ID and the section code
def insert_student_tracked_section(cursor: sqlite3.Cursor, student_id: int, course_code: str, section_number: str) -> str:
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
    return "Section added to tracked sections"

# Utility function to recursively get all data related to a target entry in a table based on the hierarchy of the database schema, starting from the target entry and including all entries that reference it as a foreign key, along with their relevant linked data based on the hierarchy, and returning this information in a structured format that indicates the relationships between the data
# Note: Don't use this on course catalog or major/minor catalog entries, as the amount of related data can be very large and may cause performance issues. This is best used on more specific entries, such as a specific course offering or a specific student.
def get_data_with_hierarchy(cursor: sqlite3.Cursor, table: str, targetID: int) -> dict:
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

# Utility function convert output of get_data_with_hierarchy into a readable string format
def hierarchy_data_to_string(hierarchy_data: dict) -> str:
    return _format_hierarchy_node(hierarchy_data)

# Utility function to get data with hierarchy as a string
def get_data_with_hierarchy_string(cursor: sqlite3.Cursor, table: str, targetID: str) -> str:
    hierarchy_data = get_data_with_hierarchy(cursor, table, targetID)
    return hierarchy_data_to_string(hierarchy_data)

# Utility function to get IDs of entries in a table based on a field value
def get_ids_by_field_value(cursor: sqlite3.Cursor, table: str, field: str, value: str) -> list:
    cursor.execute(f"SELECT ID FROM {table} WHERE {field} = ?", (value,))
    results = cursor.fetchall()
    return [row[0] for row in results]

# Utility function to get IDs of all entries in a table that reference a target entry as a foreign key, and return these IDs as a list
def get_ids_by_parent(cursor: sqlite3.Cursor, table: str, targetID: str) -> list:
    cursor.execute(f"SELECT ID FROM {table} WHERE ParentID = ?", (targetID,))
    results = cursor.fetchall()
    return [row[0] for row in results]

# Utility function to get IDs of all students that are advised by a target advisor, and return these IDs as a list
def get_students_by_advisor(cursor: sqlite3.Cursor, advisorID: str) -> list:
    cursor.execute("SELECT ID FROM Students WHERE AdvisorID = ?", (advisorID,))
    results = cursor.fetchall()
    return [row[0] for row in results]

# test utility functions
# TODO: make more extensive testing
if __name__ == "__main__":
    with sqlite3.connect("DumberDB.db") as conn:
        cursor = conn.cursor()

        """result = get_coops(cursor)
        print(result)

        result = get_upcoming_events(cursor)
        print(result)

        result = get_program_requirements_by_title(cursor, "Computer Science Transfer")
        print(result)

        result = get_student_basic_info(cursor, 1)
        print(result)

        result = get_student_course_history(cursor, 1)
        print(result)

        result = get_student_interests(cursor, 1)
        print(result)

        result = get_student_tracked_sections(cursor, 1)
        print(result)

        result = get_course_info_by_id(cursor, 1)
        print(result)

        result = get_courseIDs_by_filters(cursor, schemas.CourseFilters(departments=["CSC"], credits=[schemas.CreditCondition(condition="=", credits=3)], keywords=["programming"], prerequisites=["None"]))
        print(result)

        result = get_sectionIDs_by_filters(cursor, schemas.SectionFilters(course_codes=["CSC 101"], terms=[schemas.DBTerm(year=2023, season="Fall")], instructors=["Dr. Smith"], teaching_methods=["In-Person"], enrollment_capacity=[schemas.EnrollmentCondition(condition="<", enrollment=30)], enrollment=[schemas.EnrollmentCondition(condition="<", enrollment=30)], locations=["Main Campus"], meet_times=[schemas.DBMeetTime(days="MWF", start_time="10:00", end_time="11:00")], credits=[schemas.CreditCondition(condition="=", credits=3)], keywords=["programming"], prerequisites=["None"]))
        print(result)"""

        """print("Beginning tests...")

        print("\nTesting get_courseID_by_code and get_courseID_by_title...")
        course_id_by_code = get_courseID_by_code(cursor, "CSC 101")
        course_id_by_title = get_courseID_by_title(cursor, "Intro to Programming")
        if course_id_by_code and course_id_by_title:
            assert course_id_by_code == course_id_by_title, "Error: get_courseID_by_code and get_courseID_by_title returned different results"
            print(f"Success: Course ID for CSC 101: {course_id_by_code}")
        else:
            print("Error: Course not found by code or title")

        print("\nTesting get_course_info_by_id...")
        if course_id_by_code:
            course_info = get_course_info_by_id(cursor, course_id_by_code)
            print(f"Success: Course info for course ID {course_id_by_code}: {course_info}")
            print("Check that the course info includes all relevant fields and values, and that it is accurate based on the data in the database.")
        else:
            print("Error: Course ID not found, cannot test get_course_info_by_id")

        print("\nTesting get_data_with_hierarchy_string...")
        if course_id_by_code:
            hierarchy_string = get_data_with_hierarchy_string(cursor, "Courses", course_id_by_code)
            print(f"Success: Hierarchy string for course ID {course_id_by_code}: {hierarchy_string}")
        else:
            print("Error: Course ID not found, cannot test get_data_with_hierarchy_string")"""