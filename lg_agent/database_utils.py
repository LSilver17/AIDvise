import sqlite3
from lg_agent.utilities import schemas

# Utility function to get course ID by course code
def get_courseID_by_code(cursor: sqlite3.Cursor, course_code: str) -> str:
    department, number = course_code.split()

    cursor.execute("SELECT ID FROM Courses WHERE Department = ? AND Number = ?", (department, number))
    result = cursor.fetchone()
    return result[0] if result else None

# Utility function to get course ID by course title
def get_courseID_by_title(cursor: sqlite3.Cursor, course_title: str) -> str:
    cursor.execute("SELECT ID FROM Courses WHERE Title = ?", (course_title,))
    result = cursor.fetchone()
    return result[0] if result else None

# Utility function to filter courses based on certain criteria and return their IDs as a list
def get_courseIDs_by_filters(cursor: sqlite3.Cursor, filters: schemas.CourseFilters) -> list:
    query = "SELECT ID FROM CoursesOffered as co JOIN Courses as c ON co.CourseID = c.ID"
    params = []

    # If a term filter is specified, add a JOIN to the Sections table and conditions to the query to filter by the specified terms
    if filters.terms:
        query += " JOIN terms as t ON co.ParentID = t.ID WHERE 1=1"
        term_conditions = []
        for term in filters.terms:
            term_condition = "(t.Year = ? AND t.Season = ?"
            params.extend([term.year, term.season])
            if term.number is not None:
                term_condition += " AND t.Number = ?"
                params.append(term.number)
            term_condition += ")"
            term_conditions.append(term_condition)
        query += " AND (" + " OR ".join(term_conditions) + ")"
    else:
        query += " WHERE 1=1"

    # If a department filter is specified, add a condition to the query to filter by department
    if filters.departments:
        query += " AND c.Department IN ({})".format(",".join("?" for _ in filters.departments))
        params.extend(filters.departments)

    # If a credit filter is specified, add a condition to the query to filter by number of credits
    if filters.credits:
        condition = filters.credits.condition
        query += f" AND c.Credits {condition} ?"
        params.append(filters.credits.credits)

    # Execute the query with the specified conditions and return the IDs of the matching courses as a list
    cursor.execute(query, tuple(params))
    results = cursor.fetchall()
    return [row[0] for row in results]

# Utility function to get course info by course ID, including all requirements and prerequisites, and return this information as a dictionary
def get_course_info_by_id(cursor: sqlite3.Cursor, course_id: str) -> dict:
    cursor.execute("SELECT * FROM Courses WHERE ID = ?", (course_id,))
    course_info = {}
    for idx, col in enumerate(cursor.description):
        course_info[col[0]] = cursor.fetchone()[idx]
    
    return course_info

# Utility function to filter sections based on certain criteria and return their IDs as a list
def get_sectionIDs_by_filters(cursor: sqlite3.Cursor, filters: schemas.SectionFilters) -> list:
    query = "SELECT ID FROM Sections as s"
    params = []

    # If a course code and/or term filter is specified, add a JOIN to the Courses table
    if filters.course_codes or filters.terms:
        query += " JOIN CoursesOffered as co ON s.ParentID = co.ID JOIN Courses as c ON co.CourseID = c.ID"

    # If a meet time filter is specified, add a JOIN to the MeetTimes table
    if filters.meet_times:
        query += " JOIN MeetTimes as mt ON s.ID = mt.ParentID"

    # If a term filter is specified, add a JOIN to the Terms table and conditions to the query to filter by the specified terms
    if filters.terms:
        query += " JOIN Terms as t ON co.ParentID = t.ID WHERE 1=1"
        term_conditions = []
        for term in filters.terms:
            term_condition = "(t.Year = ? AND t.Season = ?"
            params.extend([term.year, term.season])
            if term.number is not None:
                term_condition += " AND t.Number = ?"
                params.append(term.number)
            term_condition += ")"
            term_conditions.append(term_condition)
        query += " AND (" + " OR ".join(term_conditions) + ")"
    else:
        query += " WHERE 1=1"
    
    # If a course code filter is specified, add conditions to the query to filter by the specified course codes
    if filters.course_codes:
        course_code_conditions = []
        for course_code in filters.course_codes:
            department, number = course_code.split()
            course_code_conditions.append("(c.Department = ? AND c.Number = ?)")
            params.extend([department, number])
        query += " AND (" + " OR ".join(course_code_conditions) + ")"
    
    # If an instructor filter is specified, add conditions to the query to filter by the specified instructors
    if filters.instructors:
        instructor_conditions = []
        for instructor in filters.instructors:
            instructor_conditions.append("(s.Instructor = ?)")
            params.append(instructor)
        query += " AND (" + " OR ".join(instructor_conditions) + ")"
    
    # If a teaching method filter is specified, add conditions to the query to filter by the specified teaching methods
    if filters.teaching_methods:
        teaching_method_conditions = []
        for method in filters.teaching_methods:
            teaching_method_conditions.append("(s.TeachingMethod = ?)")
            params.append(method)
        query += " AND (" + " OR ".join(teaching_method_conditions) + ")"

    # If an enrollment capacity filter is specified, add a condition to the query to filter by enrollment capacity
    if filters.enrollment_capacity:
        condition = filters.enrollment_capacity.condition
        query += f" AND s.EnrollmentCapacity {condition} ?"
        params.append(filters.enrollment_capacity.enrollment)

    # If a current enrollment filter is specified, add a condition to the query to filter by current enrollment
    if filters.enrollment:
        condition = filters.enrollment.condition
        query += f" AND s.CurrentEnrollment {condition} ?"
        params.append(filters.enrollment.enrollment)

    # If a location filter is specified, add conditions to the query to filter by the specified locations
    if filters.locations:
        location_conditions = []
        for location in filters.locations:
            location_conditions.append("(s.Location = ?)")
            params.append(location)
        query += " AND (" + " OR ".join(location_conditions) + ")"
    
    # If a meet time filter is specified, add conditions to the query to filter by the specified meet times
    if filters.meet_times:
        meet_time_conditions = []
        for meet_time in filters.meet_times:
            meet_time_condition = "(mt.Days = ? AND mt.StartTime = ? AND mt.EndTime = ?)"
            params.extend([meet_time.days, meet_time.start_time, meet_time.end_time])
            meet_time_conditions.append(meet_time_condition)
        query += " AND (" + " OR ".join(meet_time_conditions) + ")"

    # Execute the query with the specified conditions and return the IDs of the matching sections as a list
    cursor.execute(query, tuple(params))
    results = cursor.fetchall()
    return [row[0] for row in results]

# Utility function to recursively get all data related to a target entry in a table based on the hierarchy of the database schema, starting from the target entry and including all entries that reference it as a foreign key, along with their relevant linked data based on the hierarchy, and returning this information in a structured format that indicates the relationships between the data
# Note: Don't use this on course catalog or major/minor catalog entries, as the amount of related data can be very large and may cause performance issues. This is best used on more specific entries, such as a specific course offering or a specific student.
def get_data_with_hierarchy(cursor: sqlite3.Cursor, table: str, targetID: str) -> dict:
    results = {}
    entry = {}

    results["entry"] = table + ": " + targetID

    # Get the entry from the target table that corresponds to the target and add its fields and values to the results
    for row in cursor.execute(f"SELECT * FROM {table} WHERE ID = ?", (targetID,)):
        for idx, col in enumerate(cursor.description) if col[0] != "ID" and col[0] != "ParentID" and row[idx] is not None else []:
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