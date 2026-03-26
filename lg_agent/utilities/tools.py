from langchain_core.tools import tool
from lg_agent.utilities.state import AdvisorState
import database_utils
import schemas
import sqlite3

# Database query tools
@tool("course_query_by_code", description="Tool for getting information about a specific course from the database. The input is the course code (e.g. \"CSCI 101\") and the output is a string containing the relevant information about the course, including department, course number, title, description, prerequisites, and credits.", return_direct=True)
def course_query_tool_by_code(cursor: sqlite3.Cursor, course_code: str) -> str:
    course_id = database_utils.get_courseID_by_code(cursor, course_code)
    if course_id:
        course_info = database_utils.get_data_with_hierarchy_string(cursor, "Courses", course_id)
        return course_info
    else:
        return f"No course found with code {course_code}."

@tool("course_query_by_title", description="Like the course_query_by_code tool, but searches by title instead of code.", return_direct=True)
def course_query_tool_by_title(cursor: sqlite3.Cursor, course_title: str) -> str:
    course_id = database_utils.get_courseID_by_title(cursor, course_title)
    if course_id:
        course_info = database_utils.get_data_with_hierarchy_string(cursor, "Courses", course_id)
        return course_info
    else:
        return f"No course found with title {course_title}."

@tool("course_filter", description="Tool for filtering courses based on certain criteria. The input is a set of filters and the output is a string containing a all the courses that match the specified criteria and relivent information about them.", return_direct=True)
def course_filter_tool(cursor: sqlite3.Cursor, filters: schemas.CourseFilters = None) -> str:
    course_ids = database_utils.get_courseIDs_by_filters(cursor, filters)
    if course_ids:
        courses_info = []
        for course_id in course_ids:
            course_info = database_utils.get_data_with_hierarchy_string(cursor, "Courses", course_id)
            courses_info.append(course_info)
        return "\n\n".join(courses_info)
    else:
        return "No courses found matching the specified criteria."

@tool("section_filter", description="Tool for filtering sections based on certain criteria. The input is a set of filters and the output is a string containing the relevant information about the filtered sections.", return_direct=True)
def section_filter_tool(cursor: sqlite3.Cursor, filters: schemas.SectionFilters = None) -> str:
    section_ids = database_utils.get_sectionIDs_by_filters(cursor, filters)
    if section_ids:
        sections_info = []
        for section_id in section_ids:
            section_info = database_utils.get_data_with_hierarchy_string(cursor, "Sections", section_id)
            sections_info.append(section_info)
        return "\n\n".join(sections_info)
    else:
        return "No sections found matching the specified criteria."
    
# TODO: add more database tools

db_tools = [course_query_tool_by_code, course_query_tool_by_title, course_filter_tool, section_filter_tool]