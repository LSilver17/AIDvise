# Copyright 2026 Luca Silver

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
from datetime import datetime
import utilities.schemas as schemas
import database_utils
import json

TOOL_CONFIG_PATH = os.path.join(root_dir, "tool_config.json")

with open(TOOL_CONFIG_PATH, "r") as f:
    TOOL_CONFIG = json.load(f)

# misc tools
@tool("get_current_time", description="Tool for getting the current date and time. The output is a string containing the current date and time.", return_direct=True)
def get_current_time_tool() -> str:
    """
    Tool for getting the current date and time. 
    
    Returns: 
        str -- A string containing the current date and time:
            Format: "YYYY-MM-DD HH:MM:SS".
    """
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

# Database query tools
@tool("course_query_by_code", description="Tool for getting information about a specific course from the database. The input is the course code (e.g. \"CSCI 101\") and the output is a string containing the relevant information about the course, including department, course number, title, description, prerequisites, and credits.", return_direct=True)
def course_query_tool_by_code(course_code: str) -> str:
    """
    Tool for getting information about a specific course from the database.

    Args:
        course_code (str) -- The code of the course to query:
            Format: 3-letter department code followed by 3-digit course number (e.g. "CSC 101" | "CSC101").
    Returns:
        str -- A string containing the relevant information about the course:
            Format: {
                "Department": str (3-letter),
                "Course Number": int (3-digit),
                "Title": str,
                "Description": str,
                "Prerequisites": list[str],
                "Credits": int
            }
            If no course is found with the given code, returns a message indicating that no course was found.
    """
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
    """
    Tool for getting information about a specific course from the database.

    Args:
        course_title (str) -- The title of the course to query (e.g. "Introduction to Computer Science").
    Returns:
        str -- A string containing the relevant information about the course:
            Format: {
                "Department": str (3-letter),
                "Course Number": int (3-digit),
                "Title": str,
                "Description": str,
                "Prerequisites": list[str],
                "Credits": int
            }
            If no course is found with the given title, returns a message indicating that no course was found.
    """    
    with __connect() as conn:
        cursor = conn.cursor()
        if course_title == "Coperative Work Experience":
            coops = database_utils.get_coops(cursor)
            return f"There are multiple courses with the title 'Cooperative Work Experience'. Here is a list of them: {', '.join(coops)}. Please try agein using the course code to specify which one you want information about."
        course_id = database_utils.get_courseID_by_title(cursor, course_title)
        if course_id:
            course_info = database_utils.get_course_info_by_id(cursor, course_id)
            return course_info
        else:
            return f"No course found with title {course_title}."

@tool("course_filter", description="Tool for filtering courses based on certain criteria. The input is a set of filters and the output is a string containing a all the courses that match the specified criteria and relivent information about them.", return_direct=True)
def course_filter_tool(filters: schemas.CourseFilters = None) -> str:
    """
    Tool for filtering courses based on specified criteria.

    Args:
        filters (schemas.CourseFilters) -- A set of filters to apply when querying for courses:
            Format: {
                "terms": List[
                    {
                        "year": int,
                        "season": "Fall" | "Spring" | "Summer",
                        "number": int | None
                    }
                ],
                "departments": List[str], (IE: CSC, MTH, etc.)
                "credits": List[
                    {
                        "condition": "=" | ">" | "<" | ">=" | "<=" | "!=",
                        "credits": int
                    }
                ]
            }
            If no filters are needed, this can be left blank or set to None.
    Returns:
        str -- A string containing all the courses that match the specified criteria and relevant information about them:
            Format: List[{
                "Department": str (3-letter),
                "Course Number": int (3-digit),
                "Title": str,
                "Description": str,
                "Prerequisites": list[str],
                "Credits": int
            }]
    """
    
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
    """
    Tool for filtering sections based on specified criteria.

    Args:
        filters (schemas.SectionFilters) -- A set of filters to apply when querying for sections:
            Format: {
                "terms": List[
                    {
                        "year": int,
                        "season": "Fall" | "Spring" | "Summer",
                        "number": int | None
                    }
                ],
                "course_codes": List[str], (IE: CSC 101, MTH 101, etc.)
                "instructors": List[str],
                "teaching_methods": List[str], (IE: Lecture, Lab, Online, etc.)
                "enrollment_capacity": List[
                    {
                        "condition": "=" | ">" | "<" | ">=" | "<=" | "!=",
                        "enrollment_capacity": int
                    }
                ],
                "enrollment": List[
                    {
                        "condition": "=" | ">" | "<" | ">=" | "<=" | "!=",
                        "enrollment": int
                    }
                ],
                "locations": List[str],
                "meet_times": List[
                    {
                        "days": str (e.g. MW, TR, F, etc.),
                        "start_time": str (24-hour format e.g. 14:00),
                        "end_time": str (24-hour format e.g. 15:15)
                    }
                ]
            }
            If no filters are needed, this can be left blank or set to None.
    """
    
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
    """
    Tool for getting basic information about the current (student) user.

    Args:
        runtime (ToolRuntime) -- The runtime object for the tool, which contains the state of the agent, including the student ID of the current user.
    Returns:
        str -- A string containing the relevant information about the student:
            Format: {
                "Name": str,
                "Advisor": str,
                "GPA": float,
                "Total Credits": int,
                "Programs of Study": List[str]
            }
    """

    with __connect() as conn:
        cursor = conn.cursor()
        student_info = database_utils.get_student_basic_info(cursor, runtime.state["user_id"])
        return json.dumps(student_info)

@tool("student_course_history", description="Tool for getting the course codes and titles for all courses a student has taken. The output is a list of courses taken.", return_direct=True)
def get_student_course_history_tool(runtime: ToolRuntime) -> str:
    """
    Tool for getting the course history for the current (student) user.

    Args:
        runtime (ToolRuntime) -- The runtime object for the tool, which contains the state of the agent, including the student ID of the current user.
    
    """
    
    with __connect() as conn:
        cursor = conn.cursor()
        course_history = database_utils.get_student_course_history(cursor, runtime.state["user_id"])
        return json.dumps(course_history)

@tool("student_interests", description="Tool for getting a student's interests. The output is a list of interests.", return_direct=True)
def get_student_interests_tool(runtime: ToolRuntime) -> str:
    with __connect() as conn:
        cursor = conn.cursor()
        interests = database_utils.get_student_interests(cursor, runtime.state["user_id"])
        return json.dumps(interests)

@tool("student_tracked_sections", description="Tool for getting the sections a student is currently tracking. The output is a list of tracked sections.", return_direct=True)
def get_student_tracked_sections_tool(runtime: ToolRuntime) -> str:
    with __connect() as conn:
        cursor = conn.cursor()
        tracked_sections = database_utils.get_student_tracked_sections(cursor, runtime.state["user_id"])
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


db_tools = [get_current_time_tool if TOOL_CONFIG["s-db-tools"]["get_current_time_tool"] else None,
            course_query_tool_by_code if TOOL_CONFIG["s-db-tools"]["course_query_tool_by_code"] else None,
            course_query_tool_by_title if TOOL_CONFIG["s-db-tools"]["course_query_tool_by_title"] else None,
            course_filter_tool if TOOL_CONFIG["s-db-tools"]["course_filter_tool"] else None,
            section_filter_tool if TOOL_CONFIG["s-db-tools"]["section_filter_tool"] else None,
            get_student_basic_info_tool if TOOL_CONFIG["s-db-tools"]["get_student_basic_info_tool"] else None,
            get_student_course_history_tool if TOOL_CONFIG["s-db-tools"]["get_student_course_history_tool"] else None,
            get_student_interests_tool if TOOL_CONFIG["s-db-tools"]["get_student_interests_tool"] else None,
            get_student_tracked_sections_tool if TOOL_CONFIG["s-db-tools"]["get_student_tracked_sections_tool"] else None,
            get_program_requirements_tool if TOOL_CONFIG["s-db-tools"]["get_program_requirements_tool"] else None,
            get_upcoming_events_tool if TOOL_CONFIG["s-db-tools"]["get_upcoming_events_tool"] else None,
            get_event_dates_tool if TOOL_CONFIG["s-db-tools"]["get_event_dates_tool"] else None]

@tool("web_search", description="Tool for performing web searches. The input is a search query and the output is a list of search results with sources (limited to top 3 results).", return_direct=True)
def web_search_tool(query: str) -> str:
    wrapper = DuckDuckGoSearchAPIWrapper(region="us-en", time="d", max_results=3)
    search = DuckDuckGoSearchResults(wrapper=wrapper, output_format="list")
    return search.invoke(query)

web_tools = [web_search_tool if TOOL_CONFIG["web-tools"]["web_search_tool"] else None]

@tool("insert_student_interests", description="Tool for inserting a new interest for a student. The input is an interest to add, and the output is a confirmation message. Always check if a similar interest already exists in the database before adding it.", return_direct=True)
def insert_student_interests_tool(runtime: ToolRuntime, interest: str) -> str:
    with __connect() as conn:
        cursor = conn.cursor()
        return database_utils.insert_student_interests(cursor, runtime.state["user_id"], [interest])

@tool("insert_student_tracked_sections", description="Tool for inserting a new tracked section for a student. The input is the course code and section number for the section to track. The output is a confirmation message.", return_direct=True)
def insert_student_tracked_sections_tool(runtime: ToolRuntime, course_code: str, section_id: str) -> str:
    with __connect() as conn:
        cursor = conn.cursor()
        return database_utils.insert_student_tracked_section(cursor, runtime.state["user_id"], course_code, section_id)
        
insertion_tools = [get_student_interests_tool if TOOL_CONFIG["insert-tools"]["get_student_interests_tool"] else None,
                    get_student_tracked_sections_tool if TOOL_CONFIG["insert-tools"]["get_student_tracked_sections_tool"] else None,
                    insert_student_interests_tool if TOOL_CONFIG["insert-tools"]["insert_student_interests_tool"] else None,
                    insert_student_tracked_sections_tool if TOOL_CONFIG["insert-tools"]["insert_student_tracked_sections_tool"] else None]

# alt db tools for chatbot used by advisor

@tool("get_student_id_by_name", description="Tool for getting a student's ID based on their name. The input is the student's name and the output is the student's ID. Only works for students who have the current user as their advisor.", return_direct=True)
def get_student_id_by_name_tool(runtime: ToolRuntime, student_name: str) -> str:
    with __connect() as conn:
        cursor = conn.cursor()
        advisor_id = cursor.execute("SELECT ID FROM Advisors WHERE ParentID = ?", (runtime.state["user_id"],)).fetchone()
        if advisor_id is None:
            return f"No advisor found with user ID {runtime.state['user_id']}."
        cursor.execute("SELECT ID FROM Students WHERE name = ? and AdvisorID = ?", (student_name, advisor_id[0]))
        student_id = cursor.fetchone()
        if student_id:
            return json.dumps({"student_id": student_id[0]})
        else:
            return f"No student found with name {student_name}."

@tool("get_advisor_students", description="Tool for getting a list of the students assigned to the current advisor. The output is a list of student names and their IDs.", return_direct=True)
def get_advisor_students_tool(runtime: ToolRuntime) -> str:
    with __connect() as conn:
        cursor = conn.cursor()
        advisor_id = cursor.execute("SELECT ID FROM Advisors WHERE ParentID = ?", (runtime.state["user_id"],)).fetchone()
        if advisor_id is None:
            return f"No advisor found with user ID {runtime.state['user_id']}."
        cursor.execute("SELECT Name, ID FROM Students WHERE AdvisorID = ?", (advisor_id[0],))
        students = cursor.fetchall()
        if students:
            student_info = [{"name": student[0], "id": student[1]} for student in students]
            return json.dumps({"students": student_info})
        else:
            return "No students found for the current advisor."

@tool("student_basic_info", description="Tool for getting a student's basic information, including their name, GPA, total credits, and programs of study. The output is a string containing the relevant information. Only works for students who have the current user as their advisor.", return_direct=True)
def a_get_student_basic_info_tool(runtime: ToolRuntime, student_id: int) -> str:
    with __connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT AdvisorID FROM Students WHERE ID = ?", (student_id,))
        s_advisor_id = cursor.fetchone()
        u_advisor_id = cursor.execute("SELECT ID FROM Advisors WHERE ParentID = ?", (runtime.state["user_id"],)).fetchone()
        if s_advisor_id is None:
            return f"No student found with ID {student_id}"
        elif s_advisor_id[0] != u_advisor_id[0]:
            return f"Student with ID {student_id} is not assigned to the current user."
        student_info = database_utils.get_student_basic_info(cursor, student_id)
        return json.dumps(student_info)

@tool("student_course_history", description="Tool for getting the course codes and titles for all courses a student has taken. The output is a list of courses taken. Only works for students who have the current user as their advisor.", return_direct=True)
def a_get_student_course_history_tool(runtime: ToolRuntime, student_id: int) -> str:
    with __connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT AdvisorID FROM Students WHERE ID = ?", (student_id,))
        s_advisor_id = cursor.fetchone()
        u_advisor_id = cursor.execute("SELECT ID FROM Advisors WHERE ParentID = ?", (runtime.state["user_id"],)).fetchone()
        if s_advisor_id is None:
            return f"No student found with ID {student_id}"
        elif s_advisor_id[0] != u_advisor_id[0]:
            return f"Student with ID {student_id} is not assigned to the current user."
        course_history = database_utils.get_student_course_history(cursor, student_id)
        return json.dumps(course_history)

@tool("student_interests", description="Tool for getting a student's interests. The output is a list of interests. Only works for students who have the current user as their advisor.", return_direct=True)
def a_get_student_interests_tool(runtime: ToolRuntime, student_id: int) -> str:
    with __connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT AdvisorID FROM Students WHERE ID = ?", (student_id,))
        s_advisor_id = cursor.fetchone()
        u_advisor_id = cursor.execute("SELECT ID FROM Advisors WHERE ParentID = ?", (runtime.state["user_id"],)).fetchone()
        if s_advisor_id is None:
            return f"No student found with ID {student_id}"
        elif s_advisor_id[0] != u_advisor_id[0]:
            return f"Student with ID {student_id} is not assigned to the current user."
        interests = database_utils.get_student_interests(cursor, student_id)
        return json.dumps(interests)

@tool("student_tracked_sections", description="Tool for getting the sections a student is currently tracking. The output is a list of tracked sections. Only works for students who have the current user as their advisor.", return_direct=True)
def a_get_student_tracked_sections_tool(runtime: ToolRuntime, student_id: int) -> str:
    with __connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT AdvisorID FROM Students WHERE ID = ?", (student_id,))
        s_advisor_id = cursor.fetchone()
        u_advisor_id = cursor.execute("SELECT ID FROM Advisors WHERE ParentID = ?", (runtime.state["user_id"],)).fetchone()
        if s_advisor_id is None:
            return f"No student found with ID {student_id}"
        elif s_advisor_id[0] != u_advisor_id[0]:
            return f"Student with ID {student_id} is not assigned to the current user."
        tracked_sections = database_utils.get_student_tracked_sections(cursor, student_id)
        return json.dumps(tracked_sections)

alt_db_tools = [get_current_time_tool if TOOL_CONFIG["a-db-tools"]["get_current_time_tool"] else None,
                 course_query_tool_by_code if TOOL_CONFIG["a-db-tools"]["course_query_tool_by_code"] else None,
                 course_query_tool_by_title if TOOL_CONFIG["a-db-tools"]["course_query_tool_by_title"] else None,
                 course_filter_tool if TOOL_CONFIG["a-db-tools"]["course_filter_tool"] else None,
                 section_filter_tool if TOOL_CONFIG["a-db-tools"]["section_filter_tool"] else None,
                 get_student_id_by_name_tool if TOOL_CONFIG["a-db-tools"]["get_student_id_by_name_tool"] else None,
                 get_advisor_students_tool if TOOL_CONFIG["a-db-tools"]["get_advisor_students_tool"] else None,
                 a_get_student_basic_info_tool if TOOL_CONFIG["a-db-tools"]["a_get_student_basic_info_tool"] else None,
                 a_get_student_course_history_tool if TOOL_CONFIG["a-db-tools"]["a_get_student_course_history_tool"] else None,
                 a_get_student_interests_tool if TOOL_CONFIG["a-db-tools"]["a_get_student_interests_tool"] else None,
                 a_get_student_tracked_sections_tool if TOOL_CONFIG["a-db-tools"]["a_get_student_tracked_sections_tool"] else None,
                 get_program_requirements_tool if TOOL_CONFIG["a-db-tools"]["get_program_requirements_tool"] else None,
                 get_upcoming_events_tool if TOOL_CONFIG["a-db-tools"]["get_upcoming_events_tool"] else None,
                 get_event_dates_tool if TOOL_CONFIG["a-db-tools"]["get_event_dates_tool"] else None]
