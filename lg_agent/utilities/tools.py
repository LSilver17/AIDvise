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
from bs4 import BeautifulSoup
from pydantic_core import ValidationError
import utilities.schemas as schemas
import database_utils
import requests
import json

TOOL_CONFIG_PATH = os.path.join(root_dir, "tool_config.json")

with open(TOOL_CONFIG_PATH, "r") as f:
    TOOL_CONFIG = json.load(f)

DEPARTMENT_LIST_PATH = os.path.join(root_dir, "department_mapping.json")

with open(DEPARTMENT_LIST_PATH, "r") as f:
    DEPARTMENT_LIST = {"departments": []}
    DEPARTMENT_LIST["departments"] = json.load(f)

ERROR_LOG_FOLDER_PATH = os.path.join(root_dir, "tool_error_logs")
os.makedirs(ERROR_LOG_FOLDER_PATH, exist_ok=True)
ERROR_LOG_FILE_PATH = os.path.join(ERROR_LOG_FOLDER_PATH, f"tool_error_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
with open(ERROR_LOG_FILE_PATH, "w") as f:
    f.write(f"Error log created on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

# misc tools
@tool("get_current_time", description="Tool for getting the current date and time. The output is a string containing the current date and time.", return_direct=True)
def get_current_time_tool() -> str:
    """
    Tool for getting the current date and time. 
    
    Returns: 
        str -- A string containing the current date and time:
            Format: "YYYY-MM-DD HH:MM:SS".
    """
    try:
        now = datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        with open(ERROR_LOG_FILE_PATH, "a") as f:
            f.write(f"Error occurred while getting current time: {e}\n")
        return "A problem occurred. End your task early and report the issue to the planning agent."

# Database query tools
@tool("get_department_list", description="Tool for getting a list of all 3-letter department codes and their meanings. Only use this tool if you initially fail to guess the 3-letter code for a department as it can consume a lot of tokens.", return_direct=True)
def get_department_list() -> str:
    """
    Tool for getting a list of all 3-letter department codes.

    Returns:
        str -- A string containing a list of all 3-letter department codes.

    Warnings:
        This tool should only be used if you initialy fail to guess the 3-letter code for a department as it can consume a lot of tokens.
    """
    try:
        departments = DEPARTMENT_LIST["departments"]
        return json.dumps(departments)
    except Exception as e:
        with open(ERROR_LOG_FILE_PATH, "a") as f:
            f.write(f"Error occurred while getting department list: {e}\n")
        return "A problem occurred. End your task early and report the issue to the planning agent."

@tool("get_departments_in_category", description="Tool for getting a list of what types of courses are considered a part of a specified category. Options: ['Behavioral Science Elective' | 'Humanities Elective' | 'Mathematics Elective' | 'Science Elective' | 'Lab Science Elective' | 'Social Sciences Elective' | 'Liberal Arts Elective' | 'General Elective' | 'GenEd'] (GenEd = General Education)", return_direct=True)
def get_departments_in_category_tool(category: str) -> str:
    """
    Tool for getting a list of what types of courses are considered a part of a specified category.

    Args:
        category (str) -- "Behavioral Science Elective" | "Humanities Elective" | "Mathematics Elective" | "Science Elective" | "Lab Science Elective" | "Social Sciences Elective" | "Liberal Arts Elective" | "General Elective" | "GenEd"

    Returns:
        str -- A string containing a list of what types of courses are considered a part of the specified category. 
            Format: varies based on category, but generally a list of department codes (e.g. "CSC", "MTH", etc.) with any relevant course number or credit requirements.
    """
    behavioral_science = "ANT, PSY, SOC"
    humanities = "ASL, ART, COM, ENG, FRC, GER, HUM, MUS, PHI, SPN, SPH, THA"
    mathmatics = "MAT (Above 100 Level)"
    science = "BIO, BTT, CHM, PHY, SCI with at lease 3 credits"
    lab_science = "BIO, BTT, CHM, PHY with at least 4 credits (with exception of BIO 140)"
    social_science = "ANT, ECO, GEO, HST, PSC, PSY, SOS, SOC"
    liberal_arts = "ANT, ASL, ART, BIO, BTT, COM, CHM, ECO, ENG, FRC, GER, GEO, HST, HUM, MAT, (Above 100 Level), MUS, PHI, PHY, PSC, PSY, SCI, SOC, SOS, SPN, SPH, THA"
    general = "Any course (Above 100 level)"
    gen_ed = "check the course requirements for the 'General Studies' program."

    match category:
        case "Behavioral Science Elective":
            return behavioral_science
        case "Humanities Elective":
            return humanities
        case "Mathematics Elective":
            return mathmatics
        case "Science Elective":
            return science
        case "Lab Science Elective":
            return lab_science
        case "Social Sciences Elective":
            return social_science
        case "Liberal Arts Elective":
            return liberal_arts
        case "General Elective":
            return general
        case "GenEd" | "General Education":
            return gen_ed
        case _:
            return f"Invalid category {category}. Check spelling and capitalization."

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
        try:
            course_id = database_utils.get_courseID_by_code(cursor, course_code)
            if course_id:
                course_info = database_utils.get_course_info_by_id(cursor, course_id)
                return course_info
            else:
                return f"No course found with code {course_code}."
        except Exception as e:
            with open(ERROR_LOG_FILE_PATH, "a") as f:
                f.write(f"Error occurred while querying course by code: {e}\n")
            return "A problem occurred. End your task early and report the issue to the planning agent."

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
        try:
            if course_title == "Coperative Work Experience":
                coops = database_utils.get_coops(cursor)
                return f"There are multiple courses with the title 'Cooperative Work Experience'. Here is a list of them: {', '.join(coops)}. Please try agein using the course code to specify which one you want information about."
            course_id = database_utils.get_courseID_by_title(cursor, course_title)
            if course_id:
                course_info = database_utils.get_course_info_by_id(cursor, course_id)
                return course_info
            else:
                return f"No course found with title {course_title}."
        except Exception as e:
            with open(ERROR_LOG_FILE_PATH, "a") as f:
                f.write(f"Error occurred while querying course by title: {e}\n")
            return "A problem occurred. End your task early and report the issue to the planning agent."

@tool("course_filter", description="Tool for filtering courses based on certain criteria. The input is a set of filters and the output is a string containing a list of all the courses that match the specified criteria and relevant information about them. Don't use this tool with overly broad filters as it can return a lot of courses and consume a lot of tokens. Always wait until you have narrowed down the filters as much as possible before using this tool.", return_direct=True)
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
                "course_codes": List[
                    {
                        "condition": "=" | ">" | "<" | ">=" | "<=" | "!=",
                        "code": str (course number to compare against, e.g. '101')
                    }
                ],
                "credits": List[
                    {
                        "condition": "=" | ">" | "<" | ">=" | "<=" | "!=",
                        "credits": int
                    }
                ]
                "keywords": List[str], (searches for keywords in course descriptions)
                "prerequisites": List[str] (searches for keywords in course prerequisites)
            }
            Filters can be left blank if no filtering is needed for a particular criterion. Never leave all filters blank.
    Returns:
        str -- A string containing all the courses that match the specified criteria and relevant information about them:
            Format: List[{
                "Department": str (3-letter),
                "Course Number": int (3-digit),
                "Title": str,
                "Prerequisites": list[str],
                "Credits": int
            }]
    
    Warnings:
        Don't use this tool with overly broad filters (eg: all courses in a given term or all courses in a department) as it can return a lot of courses and consume a lot of tokens. Always wait until you have narrowed down the filters as much as possible before using this tool.
    """
    with __connect() as conn:
        cursor = conn.cursor()
        try:
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
        except Exception as e:
            with open(ERROR_LOG_FILE_PATH, "a") as f:
                f.write(f"Error occurred while filtering courses: {e}\n")
            if isinstance(e, ValidationError):
                return f"Invalid filters provided: {e.errors()}."
            elif isinstance(e, ValueError) and "Invalid department name: " in str(e) or "Invalid course code condition: " in str(e) or "Invalid credit condition: " in str(e):
                return e
            return "A problem occurred. End your task early and report the issue to the planning agent."

@tool("get_course_description", description="Tool for getting the description of a course based on its ID. Use this tool sparingly as it can consume a lot of tokens.", return_direct=True)
def get_course_description_tool(course_id: int) -> str:
    """
    Tool for getting the description of a course based on its ID.

    Args:
        course_id (int) -- The ID of the course for which to get the description.

    Returns:
        str -- The description of the course.
    
    Warnings:
        Don't use this tool for more than a few courses at a time, as it can consume a lot of tokens.
    """
    with __connect() as conn:
        cursor = conn.cursor()
        try:
            description = database_utils.get_course_description_by_id(cursor, course_id)
            return description
        except Exception as e:
            with open(ERROR_LOG_FILE_PATH, "a") as f:
                f.write(f"Error occurred while querying course description: {e}\n")
            return "A problem occurred. End your task early and report the issue to the planning agent."

@tool("section_filter", description="Tool for filtering sections based on certain criteria. The input is a set of filters and the output is a string containing the relevant information about the filtered sections. Don't use this tool with overly broad filters (eg: all sections in a given term or all sections taught by a certain instructor) as it can return a lot of sections and consume a lot of tokens. Always wait until you have narrowed down the filters as much as possible before using this tool.", return_direct=True)
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
            Filters can be left blank if no filtering is needed for a particular criterion. Never leave all filters blank.
    
    Returns:
        str -- A string containing a list of all the sections that match the specified criteria and relevant information about them:
            Format: List[{
                "Course Code": str (e.g. "CSC 101"),
                "Section Number": str (e.g. "001"),
                "Instructor": str,
                "Teaching Method": str (e.g. "Lecture", "Lab", "Online", etc.),
                "Enrollment Capacity": int,
                "Current Enrollment": int,
                "Location": str,
                "Meet Times": List[{
                    "Days": str (e.g. MW, TR, F, etc.),
                    "Start Time": str (24-hour format e.g. 14:00),
                    "End Time": str (24-hour format e.g. 15:15)
                }]
            
    Warnings:
        Don't use this tool with overly broad filters (eg: all sections in a given term or all sections taught by a certain instructor) as it can return a lot of sections and consume a lot of tokens. Always wait until you have narrowed down the filters as much as possible before using this tool.
    """
    with __connect() as conn:
        cursor = conn.cursor()
        try:
            section_ids = database_utils.get_sectionIDs_by_filters(cursor, filters)
            if section_ids:
                sections_info = []
                for section_id in section_ids:
                    section_info = database_utils.get_section_info_by_id(cursor, section_id)
                    sections_info.append(section_info)
                info_str = json.dumps(sections_info)
                return "\n\n"+info_str
            else:
                return "No sections found matching the specified criteria."
        except Exception as e:
            with open(ERROR_LOG_FILE_PATH, "a") as f:
                f.write(f"Error occurred while filtering sections: {e}\n")
                if isinstance(e, ValidationError):
                    return f"Invalid filters provided: {e.errors()}."
                elif isinstance(e, ValueError) and "Invalid enrollment capacity condition: " in str(e) or "Invalid enrollment condition: " in str(e):
                    return e
            return "A problem occurred. End your task early and report the issue to the planning agent."

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
        try:
            student_info = database_utils.get_student_basic_info(cursor, runtime.state["user_id"])
            return json.dumps(student_info)
        except Exception as e:
            with open(ERROR_LOG_FILE_PATH, "a") as f:
                f.write(f"Error occurred while fetching student basic info: {e}\n")
            return "A problem occurred. End your task early and report the issue to the planning agent."

@tool("student_course_history", description="Tool for getting the course codes and titles for all courses a student has taken. The output is a list of courses taken.", return_direct=True)
def get_student_course_history_tool(runtime: ToolRuntime) -> str:
    """
    Tool for getting the course history for the current (student) user.

    Args:
        runtime (ToolRuntime) -- The runtime object for the tool, which contains the state of the agent, including the student ID of the current user.
    
    Returns:
        str -- A string containing a list of courses the student has taken:
            Format: List[{
                "Course Code": str (e.g. "CSC 101"),
                "Course Title": str (e.g. "Introduction to Computer Science"),
                "Grade": "A" | "A-" | "B+" | "B" | "B-" | "C+" | "C" | "C-" | "D+" | "D" | "D-" | "F" | "X" | "W" | "NR" | "IP"
            }]
    """
    with __connect() as conn:
        cursor = conn.cursor()
        try:
            course_history = database_utils.get_student_course_history(cursor, runtime.state["user_id"])
            return json.dumps(course_history)
        except Exception as e:
            with open(ERROR_LOG_FILE_PATH, "a") as f:
                f.write(f"Error occurred while fetching student course history: {e}\n")
            return "A problem occurred. End your task early and report the issue to the planning agent."

@tool("student_interests", description="Tool for getting a student's interests. The output is a list of interests.", return_direct=True)
def get_student_interests_tool(runtime: ToolRuntime) -> str:
    """
    Tool for getting the interests for the current (student) user.

    Args:
        runtime (ToolRuntime) -- The runtime object for the tool, which contains the state of the agent, including the student ID of the current user.

    Returns:
        str -- A string containing a list of the student's interests:
            Format: List[str]
    """
    with __connect() as conn:
        cursor = conn.cursor()
        try:
            interests = database_utils.get_student_interests(cursor, runtime.state["user_id"])
            return json.dumps(interests)
        except Exception as e:
            with open(ERROR_LOG_FILE_PATH, "a") as f:
                f.write(f"Error occurred while fetching student interests: {e}\n")
            return "A problem occurred. End your task early and report the issue to the planning agent."

@tool("student_tracked_sections", description="Tool for getting the sections a student is currently tracking. The output is a list of tracked sections.", return_direct=True)
def get_student_tracked_sections_tool(runtime: ToolRuntime) -> str:
    """
    Tool for getting a list of course sections the current (student) user is tracking.

    Args:
        runtime (ToolRuntime) -- The runtime object for the tool, which contains the state of the agent, including the student ID of the current user.
    
    Returns:
        str -- A string containing a list of the sections the student is currently tracking:
            Format: List[{
                "Course Code": str (e.g. "CSC 101"),
                "Section Number": str (e.g. "1"),
                "Name": str (e.g. "Introduction to Computer Science - Section 001")
            }]
    """
    with __connect() as conn:
        cursor = conn.cursor()
        try:
            tracked_sections = database_utils.get_student_tracked_sections(cursor, runtime.state["user_id"])
            return json.dumps(tracked_sections)
        except Exception as e:
            with open(ERROR_LOG_FILE_PATH, "a") as f:
                f.write(f"Error occurred while fetching student tracked sections: {e}\n")
            return "A problem occurred. End your task early and report the issue to the planning agent."

@tool("program_requirements", description="Tool for getting the course requirements for a specific program. The input is the program name and the output is a list of required courses.", return_direct=True)
def get_program_requirements_tool(program_name: str) -> str:
    """
    Tool for getting the course requirements for a specific program of study.

    Args:
        program_name (str) -- The name of the program for which to get the requirements (e.g. "Manufacturing Technology").
    
    Returns:
        str -- A string containing a list of the course requirements for the specified program:
            Format: List[
                List of course options and elective options seperated by OR
                    Format of course option: Dep
            ]
            If no program is found with the given name, returns a message indicating that no program was found.
    """
    with __connect() as conn:
        cursor = conn.cursor()
        try:
            program_requirements = database_utils.get_program_requirements_by_title(cursor, program_name)
            return json.dumps(program_requirements)
        except Exception as e:
            with open(ERROR_LOG_FILE_PATH, "a") as f:
                f.write(f"Error occurred while fetching program requirements: {e}\n")
            return "A problem occurred. End your task early and report the issue to the planning agent."

@tool("upcoming_events", description="Tool for getting a list of upcoming events. The output is a list of upcoming events with their names and descriptions.", return_direct=True)
def get_upcoming_events_tool() -> str:
    with __connect() as conn:
        cursor = conn.cursor()
        try:
            upcoming_events = database_utils.get_upcoming_events(cursor)
            return json.dumps(upcoming_events)
        except Exception as e:
            with open(ERROR_LOG_FILE_PATH, "a") as f:
                f.write(f"Error occurred while fetching upcoming events: {e}\n")
            return "A problem occurred. End your task early and report the issue to the planning agent."

@tool("event_dates", description="Tool for getting the dates for a specific event. The input is the event name and the output is a list of dates and their locations for that event.", return_direct=True)
def get_event_dates_tool(event_name: str) -> str:
    with __connect() as conn:
        cursor = conn.cursor()
        try:
            event_dates = database_utils.get_event_dates_by_name(cursor, event_name)
            return json.dumps(event_dates)
        except Exception as e:
            with open(ERROR_LOG_FILE_PATH, "a") as f:
                f.write(f"Error occurred while fetching event dates: {e}\n")
            return "A problem occurred. End your task early and report the issue to the planning agent."

@tool("web_search", description="Tool for performing web searches. The input is a search query and the maximum number of results to return. The output is a list of search results with sources.", return_direct=True)
def web_search_tool(query: str, max_results: int = 3) -> str:
    wrapper = DuckDuckGoSearchAPIWrapper(region="us-en", time="d", max_results=max_results)
    search = DuckDuckGoSearchResults(wrapper=wrapper, output_format="list")
    return search.invoke(query)

@tool("get_web_page_content", description="Tool for getting the text content of a web page. The input is the URL of the web page and the maximum number of characters to return. The output is a string containing the text content of the web page. Use this tool sparingly as it can consume a lot of tokens.", return_direct=True)
def get_web_page_content_tool(url: str, max_chars: int = 3000) -> str:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"Error fetching from {url}: {e}"
    soup = BeautifulSoup(response.text, 'html.parser')

    for script in soup(["script", "style, noscript"]):
        script.decompose()
    
    text = soup.get_text(separator=' ')
    text = ' '.join(text.split())
    if len(text) > max_chars:
        return text[:max_chars] + "... [truncated]"
    return text

@tool("insert_student_interests", description="Tool for inserting a new interest for a student. The input is an interest to add, and the output is a confirmation message. Always check if a similar interest already exists in the database before adding it.", return_direct=True)
def insert_student_interests_tool(runtime: ToolRuntime, interest: str) -> str:
    with __connect() as conn:
        cursor = conn.cursor()
        try:
            return database_utils.insert_student_interests(cursor, runtime.state["user_id"], [interest])
        except Exception as e:
            with open(ERROR_LOG_FILE_PATH, "a") as f:
                f.write(f"Error occurred while inserting student interests: {e}\n")
            return "A problem occurred. End your task early and report the issue to the planning agent."

@tool("insert_student_tracked_sections", description="Tool for inserting a new tracked section for a student. The input is the course code and section number for the section to track. The output is a confirmation message.", return_direct=True)
def insert_student_tracked_sections_tool(runtime: ToolRuntime, course_code: str, section_id: str) -> str:
    with __connect() as conn:
        cursor = conn.cursor()
        try:
            return database_utils.insert_student_tracked_section(cursor, runtime.state["user_id"], course_code, section_id)
        except Exception as e:
            with open(ERROR_LOG_FILE_PATH, "a") as f:
                f.write(f"Error occurred while inserting student tracked sections: {e}\n")
            return "A problem occurred. End your task early and report the issue to the planning agent."

# alt db tools for chatbot used by advisor

@tool("get_student_id_by_name", description="Tool for getting a student's ID based on their name. The input is the student's name and the output is the student's ID. Only works for students who have the current user as their advisor.", return_direct=True)
def get_student_id_by_name_tool(runtime: ToolRuntime, student_name: str) -> str:
    with __connect() as conn:
        cursor = conn.cursor()
        try:
            advisor_id = cursor.execute("SELECT ID FROM Advisors WHERE ParentID = ?", (runtime.state["user_id"],)).fetchone()
            if advisor_id is None:
                return f"No advisor found with user ID {runtime.state['user_id']}."
            cursor.execute("SELECT ID FROM Students WHERE name = ? and AdvisorID = ?", (student_name, advisor_id[0]))
            student_id = cursor.fetchone()
            if student_id:
                return json.dumps({"student_id": student_id[0]})
            else:
                return f"No student found with name {student_name}."
        except Exception as e:
            with open(ERROR_LOG_FILE_PATH, "a") as f:
                f.write(f"Error occurred while getting student ID by name: {e}\n")
            return "A problem occurred. End your task early and report the issue to the planning agent."

@tool("get_advisor_students", description="Tool for getting a list of the students assigned to the current advisor. The output is a list of student names and their IDs.", return_direct=True)
def get_advisor_students_tool(runtime: ToolRuntime) -> str:
    with __connect() as conn:
        cursor = conn.cursor()
        try:
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
        except Exception as e:
            with open(ERROR_LOG_FILE_PATH, "a") as f:
                f.write(f"Error occurred while getting advisor students: {e}\n")
            return "A problem occurred. End your task early and report the issue to the planning agent."

@tool("student_basic_info", description="Tool for getting a student's basic information, including their name, GPA, total credits, and programs of study. The output is a string containing the relevant information. Only works for students who have the current user as their advisor.", return_direct=True)
def a_get_student_basic_info_tool(runtime: ToolRuntime, student_id: int) -> str:
    with __connect() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT AdvisorID FROM Students WHERE ID = ?", (student_id,))
            s_advisor_id = cursor.fetchone()
            u_advisor_id = cursor.execute("SELECT ID FROM Advisors WHERE ParentID = ?", (runtime.state["user_id"],)).fetchone()
            if s_advisor_id is None:
                return f"No student found with ID {student_id}"
            elif s_advisor_id[0] != u_advisor_id[0]:
                return f"Student with ID {student_id} is not assigned to the current user."
            student_info = database_utils.get_student_basic_info(cursor, student_id)
            return json.dumps(student_info)
        except Exception as e:
            with open(ERROR_LOG_FILE_PATH, "a") as f:
                f.write(f"Error occurred while fetching student basic info: {e}\n")
            return "A problem occurred. End your task early and report the issue to the planning agent."

@tool("student_course_history", description="Tool for getting the course codes and titles for all courses a student has taken. The output is a list of courses taken. Only works for students who have the current user as their advisor.", return_direct=True)
def a_get_student_course_history_tool(runtime: ToolRuntime, student_id: int) -> str:
    with __connect() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT AdvisorID FROM Students WHERE ID = ?", (student_id,))
            s_advisor_id = cursor.fetchone()
            u_advisor_id = cursor.execute("SELECT ID FROM Advisors WHERE ParentID = ?", (runtime.state["user_id"],)).fetchone()
            if s_advisor_id is None:
                return f"No student found with ID {student_id}"
            elif s_advisor_id[0] != u_advisor_id[0]:
                return f"Student with ID {student_id} is not assigned to the current user."
            course_history = database_utils.get_student_course_history(cursor, student_id)
            return json.dumps(course_history)
        except Exception as e:
            with open(ERROR_LOG_FILE_PATH, "a") as f:
                f.write(f"Error occurred while fetching student course history: {e}\n")
            return "A problem occurred. End your task early and report the issue to the planning agent."

@tool("student_interests", description="Tool for getting a student's interests. The output is a list of interests. Only works for students who have the current user as their advisor.", return_direct=True)
def a_get_student_interests_tool(runtime: ToolRuntime, student_id: int) -> str:
    with __connect() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT AdvisorID FROM Students WHERE ID = ?", (student_id,))
            s_advisor_id = cursor.fetchone()
            u_advisor_id = cursor.execute("SELECT ID FROM Advisors WHERE ParentID = ?", (runtime.state["user_id"],)).fetchone()
            if s_advisor_id is None:
                return f"No student found with ID {student_id}"
            elif s_advisor_id[0] != u_advisor_id[0]:
                return f"Student with ID {student_id} is not assigned to the current user."
            interests = database_utils.get_student_interests(cursor, student_id)
            return json.dumps(interests)
        except Exception as e:
            with open(ERROR_LOG_FILE_PATH, "a") as f:
                f.write(f"Error occurred while fetching student interests: {e}\n")
            return "A problem occurred. End your task early and report the issue to the planning agent."

@tool("student_tracked_sections", description="Tool for getting the sections a student is currently tracking. The output is a list of tracked sections. Only works for students who have the current user as their advisor.", return_direct=True)
def a_get_student_tracked_sections_tool(runtime: ToolRuntime, student_id: int) -> str:
    with __connect() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT AdvisorID FROM Students WHERE ID = ?", (student_id,))
            s_advisor_id = cursor.fetchone()
            u_advisor_id = cursor.execute("SELECT ID FROM Advisors WHERE ParentID = ?", (runtime.state["user_id"],)).fetchone()
            if s_advisor_id is None:
                return f"No student found with ID {student_id}"
            elif s_advisor_id[0] != u_advisor_id[0]:
                return f"Student with ID {student_id} is not assigned to the current user."
            tracked_sections = database_utils.get_student_tracked_sections(cursor, student_id)
            return json.dumps(tracked_sections)
        except Exception as e:
            with open(ERROR_LOG_FILE_PATH, "a") as f:
                f.write(f"Error occurred while fetching student tracked sections: {e}\n")
            return "A problem occurred. End your task early and report the issue to the planning agent."

d_tools = [get_current_time_tool if TOOL_CONFIG["s-db-tools"]["get_current_time_tool"] else None,
           get_department_list if TOOL_CONFIG["s-db-tools"]["get_department_list_tool"] else None,
           get_departments_in_category_tool if TOOL_CONFIG["s-db-tools"]["get_departments_in_category_tool"] else None,
           course_query_tool_by_code if TOOL_CONFIG["s-db-tools"]["course_query_tool_by_code"] else None,
           course_query_tool_by_title if TOOL_CONFIG["s-db-tools"]["course_query_tool_by_title"] else None,
           course_filter_tool if TOOL_CONFIG["s-db-tools"]["course_filter_tool"] else None,
           get_course_description_tool if TOOL_CONFIG["s-db-tools"]["get_course_description_tool"] else None,
           section_filter_tool if TOOL_CONFIG["s-db-tools"]["section_filter_tool"] else None,
           get_student_basic_info_tool if TOOL_CONFIG["s-db-tools"]["get_student_basic_info_tool"] else None,
           get_student_course_history_tool if TOOL_CONFIG["s-db-tools"]["get_student_course_history_tool"] else None,
           get_student_interests_tool if TOOL_CONFIG["s-db-tools"]["get_student_interests_tool"] else None,
           get_student_tracked_sections_tool if TOOL_CONFIG["s-db-tools"]["get_student_tracked_sections_tool"] else None,
           get_program_requirements_tool if TOOL_CONFIG["s-db-tools"]["get_program_requirements_tool"] else None,
           get_upcoming_events_tool if TOOL_CONFIG["s-db-tools"]["get_upcoming_events_tool"] else None,
           get_event_dates_tool if TOOL_CONFIG["s-db-tools"]["get_event_dates_tool"] else None]

db_tools = []
for tool in d_tools:
    if tool is not None:
        db_tools.append(tool)

w_tools = [web_search_tool if TOOL_CONFIG["web-tools"]["web_search_tool"] else None, 
           get_web_page_content_tool if TOOL_CONFIG["web-tools"]["get_web_page_content_tool"] else None]

web_tools = []

for tool in w_tools:
    if tool is not None:
        web_tools.append(tool)

i_tools = [get_student_interests_tool if TOOL_CONFIG["insert-tools"]["get_student_interests_tool"] else None,
           get_student_tracked_sections_tool if TOOL_CONFIG["insert-tools"]["get_student_tracked_sections_tool"] else None,
           insert_student_interests_tool if TOOL_CONFIG["insert-tools"]["insert_student_interests_tool"] else None,
           insert_student_tracked_sections_tool if TOOL_CONFIG["insert-tools"]["insert_student_tracked_sections_tool"] else None]

insertion_tools = []

for tool in i_tools:
    if tool is not None:
        insertion_tools.append(tool)

ad_tools = [get_current_time_tool if TOOL_CONFIG["a-db-tools"]["get_current_time_tool"] else None,
            get_department_list if TOOL_CONFIG["a-db-tools"]["get_department_list_tool"] else None,
            get_departments_in_category_tool if TOOL_CONFIG["a-db-tools"]["get_departments_in_category_tool"] else None,
            course_query_tool_by_code if TOOL_CONFIG["a-db-tools"]["course_query_tool_by_code"] else None,
            course_query_tool_by_title if TOOL_CONFIG["a-db-tools"]["course_query_tool_by_title"] else None,
            course_filter_tool if TOOL_CONFIG["a-db-tools"]["course_filter_tool"] else None,
            get_course_description_tool if TOOL_CONFIG["a-db-tools"]["get_course_description_tool"] else None,
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

alt_db_tools = []
for tool in ad_tools:
    if tool is not None:
        alt_db_tools.append(tool)
