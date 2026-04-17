import sys, os
    
# adds root directory to system path if not already there
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

# adds utilities directory to system path if not already there
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from data_pipeline.database.database_dev_tools import __connect
from langchain.tools import ToolRuntime
import utilities.schemas as schemas
import database_utils
import json

# Database query tools
@tool("course_query_by_code", description="Tool for getting information about a specific course from the database. The input is the course code (e.g. \"CSCI 101\") and the output is a string containing the relevant information about the course, including department, course number, title, description, prerequisites, and credits.", return_direct=True)
def course_query_tool_by_code(course_code: str) -> str:
    with __connect() as conn:
        cursor = conn.cursor()
        course_id = database_utils.get_courseID_by_code(cursor, course_code)
        if course_id:
            course_info = database_utils.get_course_info_by_id(cursor, course_id)
            return course_info
        else:
            return f"No course found with code {course_code}."

@tool("course_query_by_title", description="Like the course_query_by_code tool, but searches by title instead of code.", return_direct=True)
def course_query_tool_by_title(course_title: str) -> str:
    with __connect() as conn:
        cursor = conn.cursor()
        course_id = database_utils.get_courseID_by_title(cursor, course_title)
        if course_id:
            course_info = database_utils.get_course_info_by_id(cursor, course_id)
            return course_info
        else:
            return f"No course found with title {course_title}."

@tool("course_filter", description="Tool for filtering courses based on certain criteria. The input is a set of filters and the output is a string containing a all the courses that match the specified criteria and relivent information about them.", return_direct=True)
def course_filter_tool(filters: schemas.CourseFilters = None) -> str:
    with __connect() as conn:
        cursor = conn.cursor()
        course_ids = database_utils.get_courseIDs_by_filters(cursor, filters)
        if course_ids:
            courses_info = []
            for course_id in course_ids:
                course_info = database_utils.get_course_info_by_id(cursor, course_id)
                courses_info.append(course_info)
            info_str = json.dumps(courses_info)
            return "\n\n"+info_str
        else:
            return "No courses found matching the specified criteria."

@tool("section_filter", description="Tool for filtering sections based on certain criteria. The input is a set of filters and the output is a string containing the relevant information about the filtered sections.", return_direct=True)
def section_filter_tool(filters: schemas.SectionFilters = None) -> str:
    with __connect() as conn:
        cursor = conn.cursor()
        section_ids = database_utils.get_sectionIDs_by_filters(cursor, filters)
        if section_ids:
            sections_info = []
            for section_id in section_ids:
                section_info = database_utils.get_data_with_hierarchy_string(cursor, "Sections", section_id)
                sections_info.append(section_info)
            info_str = json.dumps(sections_info)
            return "\n\n"+info_str
        else:
            return "No sections found matching the specified criteria."

@tool("student_basic_info", description="Tool for getting a student's basic information, including their name, Advisor, GPA, total credits, and programs of study. The output is a string containing the relevant information.", return_direct=True)
def get_student_basic_info_tool(runtime: ToolRuntime) -> str:
    with __connect() as conn:
        cursor = conn.cursor()
        student_info = database_utils.get_student_basic_info(cursor, tool_runtime.state["student_id"])
        return json.dumps(student_info)

@tool("student_course_history", description="Tool for getting the course codes and titles for all courses a student has taken. The output is a list of courses taken.", return_direct=True)
def get_student_course_history_tool(runtime: ToolRuntime) -> str:
    with __connect() as conn:
        cursor = conn.cursor()
        course_history = database_utils.get_student_course_history(cursor, tool_runtime.state["student_id"])
        return json.dumps(course_history)

@tool("student_interests", description="Tool for getting a student's interests. The output is a list of interests.", return_direct=True)
def get_student_interests_tool(runtime: ToolRuntime) -> str:
    with __connect() as conn:
        cursor = conn.cursor()
        interests = database_utils.get_student_interests(cursor, tool_runtime.state["student_id"])
        return json.dumps(interests)

@tool("student_tracked_sections", description="Tool for getting the sections a student is currently tracking. The output is a list of tracked sections.", return_direct=True)
def get_student_tracked_sections_tool(runtime: ToolRuntime) -> str:
    with __connect() as conn:
        cursor = conn.cursor()
        tracked_sections = database_utils.get_student_tracked_sections(cursor, tool_runtime.state["student_id"])
        return json.dumps(tracked_sections)

@tool("program_requirements", description="Tool for getting the course requirements for a specific program. The input is the program name and the output is a list of required courses.", return_direct=True)
def get_program_requirements_tool(program_name: str) -> str:
    with __connect() as conn:
        cursor = conn.cursor()
        program_requirements = database_utils.get_program_requirements_by_title(cursor, program_name)
        return json.dumps(program_requirements)
    
@tool("upcoming_events", description="Tool for getting a list of upcoming events. The output is a list of upcoming events with their names and descriptions.", return_direct=True)
def get_upcoming_events_tool() -> str:
    with __connect() as conn:
        cursor = conn.cursor()
        upcoming_events = database_utils.get_upcoming_events(cursor)
        return json.dumps(upcoming_events)

@tool("event_dates", description="Tool for getting the dates for a specific event. The input is the event name and the output is a list of dates and their locations for that event.", return_direct=True)
def get_event_dates_tool(event_name: str) -> str:
    with __connect() as conn:
        cursor = conn.cursor()
        event_dates = database_utils.get_event_dates_by_name(cursor, event_name)
        return json.dumps(event_dates)

db_tools = [course_query_tool_by_code, course_query_tool_by_title, course_filter_tool, section_filter_tool, get_student_basic_info_tool, get_student_course_history_tool, get_student_interests_tool, get_student_tracked_sections_tool, get_program_requirements_tool, get_upcoming_events_tool, get_event_dates_tool]

@tool("web_search", description="Tool for performing web searches. The input is a search query and the output is a list of search results with sources (limited to top 3 results).", return_direct=True)
def web_search_tool(query: str) -> str:
    wrapper = DuckDuckGoSearchAPIWrapper(region="us-en", time="d", max_results=3)
    search = DuckDuckGoSearchResults(keys_to_include=["title", "snippet"], wrapper=wrapper, output_format="list")
    return search.invoke(query)

web_tools = [web_search_tool]

@tool("insert_student_interests", description="Tool for inserting a new interest for a student. The input is an interest to add, and the output is a confirmation message. Always check if a similar interest already exists in the database before adding it.", return_direct=True)
def insert_student_interests_tool(runtime: ToolRuntime, interest: str) -> str:
    with __connect() as conn:
        cursor = conn.cursor()
        return database_utils.insert_student_interests(cursor, tool_runtime.state["student_id"], [interest])

@tool("insert_student_tracked_sections", description="Tool for inserting a new tracked section for a student. The input is the course code and section number for the section to track. The output is a confirmation message.", return_direct=True)
def insert_student_tracked_sections_tool(runtime: ToolRuntime, course_code: str, section_id: str) -> str:
    with __connect() as conn:
        cursor = conn.cursor()
        return database_utils.insert_student_tracked_section(cursor, tool_runtime.state["student_id"], course_code, section_id)
        
insertion_tools = [get_student_interests_tool, get_student_tracked_sections_tool, insert_student_interests_tool, insert_student_tracked_sections_tool]