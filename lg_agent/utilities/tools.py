"""
Copyright 2026 Luca Silver

This file contains the tool implementations for the course-planning agent. Each tool is defined as a function decorated with `@tool` from LangChain, which specifies the tool's name, description, and return behavior.

Database agent tools for student users:
- `get_current_time_tool`: Retrieves the current date and time as a formatted string.
- `get_department_list_tool`: Retrieves a list of all 3-letter department codes and their meanings.
- `get_departments_in_category_tool`: Retrieves a list of what types of courses are considered a part of a specified category.
- `course_query_tool_by_code`: Retrieves information about a specific course based on its course code.
- `course_query_tool_by_title`: Retrieves information about a specific course based on its title.
- `course_filter_tool`: Retrieves a list of courses that match specified filter criteria.
- `get_course_description_tool`: Retrieves the description of a course based on its ID.
- `section_filter_tool`: Retrieves a list of sections that match specified filter criteria.
- `get_student_basic_info_tool`: Retrieves basic profile information for the current student user, including their name, email, advisor, GPA, total credits, and programs of study.
- `get_student_course_history_tool`: Retrieves the course history for the current student user, including course codes, titles, and grades.
- `get_student_interests_tool`: Retrieves the interests for the current student user.
- `get_student_tracked_sections_tool`: Retrieves the course sections that the student user is currently tracking for openings.
- `get_program_requirements_tool`: Retrieves the course requirements for a specified program of study.
- `get_upcoming_events_tool`: Retrieves a list of upcoming events.
- `get_event_dates_tool`: Retrieves the dates for a specified event.

Database agent tools for advisor users:
- `get_current_time_tool`: Retrieves the current date and time as a formatted string.
- `get_department_list_tool`: Retrieves a list of all 3-letter department codes and their meanings.
- `get_departments_in_category_tool`: Retrieves a list of what types of courses are considered a part of a specified category.
- `course_query_tool_by_code`: Retrieves information about a specific course based on its course code.
- `course_query_tool_by_title`: Retrieves information about a specific course based on its title.
- `course_filter_tool`: Retrieves a list of courses that match specified filter criteria.
- `get_course_description_tool`: Retrieves the description of a course based on its ID.
- `section_filter_tool`: Retrieves a list of sections that match specified filter criteria.
- `get_student_id_by_name_tool`: Retrieves a student's ID based on their name. Only works for students who have the current user as their advisor.
- `get_advisor_students_tool`: Retrieves a list of students assigned to the advisor user, including their names and IDs.
- `a_get_student_basic_info_tool`: Retrieves basic profile information for a specified student who is assigned to the advisor user, including their name, email, advisor, GPA, total credits, and programs of study.
- `a_get_student_course_history_tool`: Retrieves the course history for a specified student who is assigned to the advisor user, including course codes, titles, and grades.
- `a_get_student_interests_tool`: Retrieves the current interests for a specified student who is assigned to the advisor user.
- `a_get_student_tracked_sections_tool`: Retrieves the sections that a specified student who is assigned to the advisor user is currently tracking for openings.
- `get_program_requirements_tool`: Retrieves the course requirements for a specified program of study.
- `get_upcoming_events_tool`: Retrieves a list of upcoming events.
- `get_event_dates_tool`: Retrieves the dates for a specified event.

Insertion agent tools:
- `get_student_interests_tool`: Retrieves the interests for the current student user.
- `get_student_tracked_sections_tool`: Retrieves the course sections that the student user is currently tracking for openings.
- `insert_student_interests_tool`: Inserts a new interest for the current student user.
- `insert_student_tracked_section_tool`: Inserts a new tracked section for the current student user.

Web agent tools:
- `web_search_tool`: Performs a web search for a given query and returns a list of results with sources.
- `fetch_web_page_content_tool`: Fetches and extracts the main textual content from a specified URL.

Individual tools can be disabled using the `tool_config.json` file. If a tool is disabled, it will not be registered with the agent and cannot be called by the agent's language model. This allows for dynamic control over which tools the agent has access to without needing to modify the code.
"""

import sys, os
    
# adds root directory to system path if not already there
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# adds utilities directory to system path if not already there
PARENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PARENT_DIR not in sys.path:
    sys.path.append(PARENT_DIR)

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

CONFIG_PATH = os.path.join(ROOT_DIR, "config.json")

with open(CONFIG_PATH, "r") as f:
    CONFIG = json.load(f)

TOOL_CONFIG = CONFIG["tool_select"]

DEPARTMENT_LIST_PATH = os.path.join(ROOT_DIR, "department_mapping.json")

with open(DEPARTMENT_LIST_PATH, "r") as f:
    DEPARTMENT_LIST = {"departments": []}
    DEPARTMENT_LIST["departments"] = json.load(f)

START_TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

# Helper function to ensure error_logs directory exists
def _get_error_log_path():
    """Ensure error_logs directory exists and return the path for error log file."""
    error_log_dir = os.path.join(ROOT_DIR, "error_logs")
    os.makedirs(error_log_dir, exist_ok=True)
    return os.path.join(error_log_dir, f"error_log_{START_TIMESTAMP}.txt")

@tool("get_current_time", description="Tool for getting the current date and time. The output is a string containing the current date and time.", return_direct=True)
def get_current_time_tool() -> str:
    """Return the current date and time as a formatted string.

    Returns:
        out (str): Current date and time:
            Format: "YYYY-MM-DD HH:MM:SS"
    """
    try:
        now = datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        ERROR_LOG_FILE_PATH = _get_error_log_path()
        if not os.path.exists(ERROR_LOG_FILE_PATH):
            with open(ERROR_LOG_FILE_PATH, "w") as f:
                f.write(f"Error log for {START_TIMESTAMP}\n\n")
        with open(ERROR_LOG_FILE_PATH, "a") as f:
            current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{current_timestamp}] Error occurred while getting current time: {e}\n")
        return "A problem occurred. End your task early and report the issue to the planning agent."

@tool("get_department_list", description="Tool for getting a list of all 3-letter department codes and their meanings. Only use this tool if you initially fail to guess the 3-letter code for a department as it can consume a lot of tokens.", return_direct=True)
def get_department_list_tool() -> str:
    """Return the list of 3-letter department codes.

    Returns:
        out (str): JSON-encoded list of all department mappings:
            Format: List[{
                "Code": str, 
                    Format: 3-letter department code (e.g. "CSC", "HST", etc).
                "Department": str
                    Format: Full department name corresponding to the code (e.g. "Computer Science", "History", etc).
            }]

    Warnings:
        This tool should only be used if you initialy fail to guess the 3-letter code for a department as it can consume a lot of tokens.
    """
    try:
        departments = DEPARTMENT_LIST["departments"]
        return json.dumps(departments)
    except Exception as e:
        ERROR_LOG_FILE_PATH = _get_error_log_path()
        if not os.path.exists(ERROR_LOG_FILE_PATH):
            with open(ERROR_LOG_FILE_PATH, "w") as f:
                f.write(f"Error log for {START_TIMESTAMP}\n\n")
        with open(ERROR_LOG_FILE_PATH, "a") as f:
            current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{current_timestamp}] Error occurred while getting department list: {e}\n")
        return "A problem occurred. End your task early and report the issue to the planning agent."

@tool("get_departments_in_category", description="Tool for getting a list of what types of courses are considered a part of a specified category. Options: ['Behavioral Science Elective' | 'Humanities Elective' | 'Mathematics Elective' | 'Science Elective' | 'Lab Science Elective' | 'Social Sciences Elective' | 'Liberal Arts Elective' | 'General Elective' | 'GenEd'] (GenEd = General Education)", return_direct=True)
def get_departments_in_category_tool(category: str) -> str:
    """Return department codes considered part of the specified elective/category.

    Args:
        category (str): The category to query:
            Format: one of ["Behavioral Science Elective" | "Humanities Elective" | "Mathematics Elective" | "Science Elective" | "Lab Science Elective" | "Social Sciences Elective" | "Liberal Arts Elective" | "General Elective" | "GenEd"]

    Returns:
        out (str): Comma-separated list of department codes or a short explanatory string. The exact format varies by category.
    """
    behavioral_science = "ANT, PSY, SOC"
    humanities = "ASL, ART, COM, ENG, FRC, GER, HUM, MUS, PHI, SPN, SPH, THA"
    mathematics = "MAT (Above 100 Level)"
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
            return mathematics
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
    """Return course metadata for a course identified by its course code.

    Wraps `database_utils.get_courseID_by_code` and `database_utils.get_course_info_by_id`.

    Args:
        course_code (str): The course code to look up:
            Format: "DPT NUM" | "DPTNUM" (eg. "MAT 101" or "MAT101").

    Returns:
        out (str): Either a not-found message or course metadata for the matched course:
            Format if found: {
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
                    Format: Text string from `Courses.Requirements` column describing prerequisites/requirements.
            }
            Format if not found: "No course found with code {course_code}."
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
            ERROR_LOG_FILE_PATH = _get_error_log_path()
            if not os.path.exists(ERROR_LOG_FILE_PATH):
                with open(ERROR_LOG_FILE_PATH, "w") as f:
                    f.write(f"Error log for {START_TIMESTAMP}\n\n")
            with open(ERROR_LOG_FILE_PATH, "a") as f:
                current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{current_timestamp}] Error occurred while querying course by code: {e}\n")
            return "A problem occurred. End your task early and report the issue to the planning agent."

@tool("course_query_by_title", description="Like the course_query_by_code tool, but searches by title instead of code.", return_direct=True)
def course_query_tool_by_title(course_title: str) -> str:
    """Return course metadata for a course identified by its title.

    Wraps `database_utils.get_courseID_by_title`, `database_utils.get_coops`, and
    `database_utils.get_course_info_by_id`.

    Args:
        course_title (str): The course title to look up.
            Format: Exact course title as stored in `Courses.Name` column (eg. "Introduction to Computer Science").

    Returns:
        out (str): Either a not-found/clarification message or course metadata:
            Format if found: {
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
                    Format: Text string from `Courses.Requirements` column describing prerequisites/requirements.
            }
            Format if not found: "No course found with title {course_title}."

    Warnings:
        Course-title lookup assumes titles are unique except for "Cooperative Work Experience".
        For that title, this tool returns a clarification message containing matching course IDs and asks for a code-based query.
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
            ERROR_LOG_FILE_PATH = _get_error_log_path()
            if not os.path.exists(ERROR_LOG_FILE_PATH):
                with open(ERROR_LOG_FILE_PATH, "w") as f:
                    f.write(f"Error log for {START_TIMESTAMP}\n\n")
            with open(ERROR_LOG_FILE_PATH, "a") as f:
                current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{current_timestamp}] Error occurred while querying course by title: {e}\n")
            return "A problem occurred. End your task early and report the issue to the planning agent."

@tool("course_filter", description="Tool for filtering courses based on certain criteria. The input is a set of filters and the output is a string containing a list of all the courses that match the specified criteria and relevant information about them. Don't use this tool with overly broad filters as it can return a lot of courses and consume a lot of tokens. Always wait until you have narrowed down the filters as much as possible before using this tool.", return_direct=True)
def course_filter_tool(filters: schemas.CourseFilters = None) -> str:
    """Return courses that match the provided `schemas.CourseFilters`.

    Wraps `database_utils.get_courseIDs_by_filters` then resolves each ID with
    `database_utils.get_course_info_by_id`.

    Args:
        filters (schemas.CourseFilters): Filters to apply to the course search:
            Format: {
                Optional[List[DBTerm]] terms,
                    DBTerm format: {
                        "year": int,
                            Format: 4-digit year (e.g. 2024)
                        "season": str,
                            Format: ["Fall", "Winter", "Spring", "Summer"]
                        "number": Optional[int]
                            Format: Integer term number (e.g. 1, 2, 3, etc).
                            Note: If not provided, filter matches any term number for the given year/season.
                    }
                Optional[List[str]] departments,
                    Format: Department abbreviations as stored in `Courses.Department` (e.g. ["PHY", "MAT"]).
                Optional[List[CodeCondition]] course_codes,
                    CodeCondition format: {
                        "condition": str ["=" | ">" | "<" | ">=" | "<=" | "!="],
                        "code": str
                            Format: Course number as stored in `Courses.Code` (e.g. "101", "210").
                    }
                Optional[List[CreditCondition]] credits,
                    CreditCondition format: {
                        "condition": str ["=" | ">" | "<" | ">=" | "<=" | "!="],
                        "credits": int (e.g. 3 or 4)
                    }
                Optional[List[str]] keywords,
                    Format: Keywords searched in `Courses.Description`.
                Optional[List[str]] prerequisites,
                    Format: Keywords searched in `Courses.Requirements`.
            }

    Returns:
        out (str): JSON-encoded list of course metadata dicts:
            Format: List[{
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
                    Format: Text string from `Courses.Requirements` column describing prerequisites/requirements.
            }]
            Note: If no matches are found, returns "No courses found matching the specified criteria.".

    Raises:
        ValueError: Propagated from underlying filter logic when an invalid operator is provided:
            Course code error message: "Invalid course code condition: {condition}"
            Credit error message: "Invalid credit condition: {condition}"

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
            ERROR_LOG_FILE_PATH = _get_error_log_path()
            if not os.path.exists(ERROR_LOG_FILE_PATH):
                with open(ERROR_LOG_FILE_PATH, "w") as f:
                    f.write(f"Error log for {START_TIMESTAMP}\n\n")
            with open(ERROR_LOG_FILE_PATH, "a") as f:
                current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{current_timestamp}] Error occurred while filtering courses: {e}\n")
            if isinstance(e, ValidationError):
                return f"Invalid filters provided: {e.errors()}."
            elif isinstance(e, ValueError) and "Invalid course code condition: " in str(e) or "Invalid credit condition: " in str(e):
                return e
            return "A problem occurred. End your task early and report the issue to the planning agent."

@tool("get_course_description", description="Tool for getting the description of a course based on its ID. Use this tool sparingly as it can consume a lot of tokens.", return_direct=True)
def get_course_description_tool(course_id: int) -> str:
    """Return the textual description for a course identified by `course_id`.

    Wraps `database_utils.get_course_description_by_id`.

    Args:
        course_id (int): The ID of the course to retrieve the description for:
            Format: Primary key value from `Courses.ID` column (eg. "12345").

    Returns:
        out (str): Course description as stored in `Courses.Description` for the matched course:
            Format: Text string from `Courses.Description` column describing the course.
            Note: If no course is found with that ID, returns "Course not found".

    Warnings:
        Don't use this tool for more than a few courses at a time, as it can consume a lot of tokens.
    """
    with __connect() as conn:
        cursor = conn.cursor()
        try:
            description = database_utils.get_course_description_by_id(cursor, course_id)
            return description
        except Exception as e:
            ERROR_LOG_FILE_PATH = _get_error_log_path()
            if not os.path.exists(ERROR_LOG_FILE_PATH):
                with open(ERROR_LOG_FILE_PATH, "w") as f:
                    f.write(f"Error log for {START_TIMESTAMP}\n\n")
            with open(ERROR_LOG_FILE_PATH, "a") as f:
                current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{current_timestamp}] Error occurred while querying course description: {e}\n")
            return "A problem occurred. End your task early and report the issue to the planning agent."

@tool("section_filter", description="Tool for filtering sections based on certain criteria. The input is a set of filters and the output is a string containing the relevant information about the filtered sections. Don't use this tool with overly broad filters (eg: all sections in a given term or all sections taught by a certain instructor) as it can return a lot of sections and consume a lot of tokens. Always wait until you have narrowed down the filters as much as possible before using this tool.", return_direct=True)
def section_filter_tool(filters: schemas.SectionFilters = None) -> str:
    """Return sections that match the provided `schemas.SectionFilters`.

    Wraps `database_utils.get_sectionIDs_by_filters` then resolves each ID with
    `database_utils.get_section_info_by_id`.

    Args:
        filters (schemas.SectionFilters): Filters to apply to the section search:
            Format: {
                Optional[List[DBTerm]] terms,
                    DBTerm format: {
                        "year": int,
                            Format: 4-digit year (e.g. 2024)
                        "season": str,
                            Format: ["Fall", "Winter", "Spring", "Summer"]
                        "number": Optional[int]
                            Format: Integer term number (e.g. 1, 2, 3, etc).
                            Note: If not provided, filter matches any term number for the given year/season.
                    }
                Optional[List[str]] course_codes,
                    Format: Course codes as stored in `Courses.Code` column (e.g. ["101", "210"]).
                Optional[List[str]] instructors,
                    Format: Instructor names as stored in `Sections.Instructor` column (e.g. ["Dr. Smith", "Prof. Johnson"]).
                Optional[List[str]] teaching_methods,
                    Format: Teaching methods as stored in `Sections.Method` column (e.g. ["In-Person", "Online", "Hybrid"]).
                Optional[List[EnrollmentCondition]] enrollment_capacity,
                    EnrollmentCondition format: {
                        "condition": str ["=" | ">" | "<" | ">=" | "<=" | "!="],
                        "capacity": int (e.g. 30 or 100)
                    }
                Optional[List[EnrollmentCondition]] enrollment,
                    EnrollmentCondition format: {
                        "condition": str ["=" | ">" | "<" | ">=" | "<=" | "!="],
                        "enrollment": int (e.g. 25 or 100)
                    }
                Optional[List[str]] locations,
                    Format: Location strings as stored in `Sections.Location` column (e.g. ["Building A Room 101", "Online"]).
                Optional[List[DBMeetTime]] meet_times
                    DBMeetTime format: {
                        "day": str,
                            Format: Day of the week (e.g. "Monday", "Tuesday", etc).
                        "start_time": str,
                            Format: Start time in 24-hour format (e.g. "13:00" for 1 PM).
                        "end_time": str,
                            Format: End time in 24-hour format (e.g. "14:15" for 2:15 PM).
                    }
            }
            Note: Field-level formats and operator restrictions match `database_utils.get_sectionIDs_by_filters`.

    Returns:
        out (str): JSON-encoded list of section metadata dicts:
            Format: List[{
                "ID": str,
                    Format: Primary key value from `Sections.ID` column (eg. "67890")
                "Department": str,
                    Format: Department abbreviation as stored in `Courses.Department` (e.g. "HST")
                "Code": str,
                    Format: Course number as stored in `Courses.Code` (e.g. "101")
                "Name": str,
                    Format: Course name as stored in `Courses.Name` (e.g. "Introduction to Computer Science")
                "SectionNum": str,
                    Format: Section number as stored in `Sections.SectionNumber` column (e.g. "001")
                "Instructor": str,
                    Format: Instructor name as stored in `Sections.Instructor` column (e.g. "Dr. Smith")
                "Method": str,
                    Format: Teaching method as stored in `Sections.Method` column (e.g. "In-Person", "Online", "Hybrid")
                "Location": str,
                    Format: Location string as stored in `Sections.Location` column (e.g. "Building A Room 101", "Online")
                "MaxSeats": int,
                    Format: Maximum enrollment capacity as stored in `Sections.MaxSeats` column (e.g. 30 or 100)
                "SeatsLeft": int
                    Format: Current available seats as stored in `Sections.SeatsLeft` column (e.g. 25 or 100)
            }]
            Note: If no matches are found, returns "No sections found matching the specified criteria.".

    Raises:
        ValueError: Propagated from underlying filter logic when an invalid operator is provided:
            Enrollment capacity error message: "Invalid enrollment capacity condition: {condition}"
            Current enrollment error message: "Invalid enrollment condition: {condition}"

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
            ERROR_LOG_FILE_PATH = _get_error_log_path()
            if not os.path.exists(ERROR_LOG_FILE_PATH):
                with open(ERROR_LOG_FILE_PATH, "w") as f:
                    f.write(f"Error log for {START_TIMESTAMP}\n\n")
            with open(ERROR_LOG_FILE_PATH, "a") as f:
                current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{current_timestamp}] Error occurred while filtering sections: {e}\n")
                if isinstance(e, ValidationError):
                    return f"Invalid filters provided: {e.errors()}."
                elif isinstance(e, ValueError) and "Invalid enrollment capacity condition: " in str(e) or "Invalid enrollment condition: " in str(e):
                    return e
            return "A problem occurred. End your task early and report the issue to the planning agent."

@tool("student_basic_info", description="Tool for getting a student's basic information, including their name, Advisor, GPA, total credits, and programs of study. The output is a string containing the relevant information.", return_direct=True)
def get_student_basic_info_tool(runtime: ToolRuntime) -> str:
    """Return basic profile information for the current student user.

    Wraps `database_utils.get_student_basic_info` using `runtime.state["user_id"]`.

    Args:
        runtime (ToolRuntime): Runtime state for the current tool call:
            Required key: `runtime.state["user_id"]` as a student ID.

    Returns:
        out (str): JSON-encoded student profile info:
            Format: {
                "Name": str,
                    Format: Student's full name as stored in `Students.Name` column (e.g. "John Doe")
                "Email": str,
                    Format: Student's email as stored in `Students.Email` column (e.g. "john.doe@university.edu")
                "Advisor": str,
                    Format: Student's advisor name as stored in `Students.Advisor` column (e.g. "Dr. Smith")
                "GPA": float,
                    Format: Student's current GPA as stored in `Students.GPA` column (e.g. 3.75)
                "CreditsEarned": int,
                    Format: Total number of credits earned as stored in `Students.CreditsEarned` column (e.g. 90)
                "ProgramsOfStudy": list[dict]
                    Format: List of dicts representing the student's programs of study.
                    Each dict format: {
                        "Title": str,
                            Format: Program title as stored in `ProgramsOfStudy.Title` column (e.g. "Computer Information Systems")
                        "Status": str
                            Format: Student's status in the program as stored in `StudentPrograms.Status` column (e.g. "Declared", "Undeclared", "Completed", etc)
            }
            Note: If no student is found with that ID, serialized value is {}.
    """
    with __connect() as conn:
        cursor = conn.cursor()
        try:
            student_info = database_utils.get_student_basic_info(cursor, runtime.state["user_id"])
            return json.dumps(student_info)
        except Exception as e:
            ERROR_LOG_FILE_PATH = _get_error_log_path()
            if not os.path.exists(ERROR_LOG_FILE_PATH):
                with open(ERROR_LOG_FILE_PATH, "w") as f:
                    f.write(f"Error log for {START_TIMESTAMP}\n\n")
            with open(ERROR_LOG_FILE_PATH, "a") as f:
                current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{current_timestamp}] Error occurred while fetching student basic info: {e}\n")
            return "A problem occurred. End your task early and report the issue to the planning agent."

@tool("student_course_history", description="Tool for getting the course codes and titles for all courses a student has taken. The output is a list of courses taken.", return_direct=True)
def get_student_course_history_tool(runtime: ToolRuntime) -> str:
    """Return course history for the current student user.

    Wraps `database_utils.get_student_course_history` using `runtime.state["user_id"]`.

    Args:
        runtime (ToolRuntime): Runtime state for the current tool call:
            Required key: `runtime.state["user_id"]` as a student ID.

    Returns:
        out (str): JSON-encoded list of course-history entries:
            Format: List[{
                "CourseCode": str,
                    Format: Department and course number as stored in `Courses.Department` and `Courses.Code` columns (e.g. "HST 210")
                "Name": str,
                    Format: Course name as stored in `Courses.Name` column (e.g. "World History Since 1500")
                "Grade": str
                    Format: Grade earned in the course as stored in `StudentCourses.Grade` column (e.g. "A", "B+", "Satisfactory", etc)
            }]
            Note: If no courses are found, serialized value is ["No courses taken"].
    """
    with __connect() as conn:
        cursor = conn.cursor()
        try:
            course_history = database_utils.get_student_course_history(cursor, runtime.state["user_id"])
            return json.dumps(course_history)
        except Exception as e:
            ERROR_LOG_FILE_PATH = _get_error_log_path()
            if not os.path.exists(ERROR_LOG_FILE_PATH):
                with open(ERROR_LOG_FILE_PATH, "w") as f:
                    f.write(f"Error log for {START_TIMESTAMP}\n\n")
            with open(ERROR_LOG_FILE_PATH, "a") as f:
                current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{current_timestamp}] Error occurred while fetching student course history: {e}\n")
            return "A problem occurred. End your task early and report the issue to the planning agent."

@tool("student_interests", description="Tool for getting a student's interests. The output is a list of interests.", return_direct=True)
def get_student_interests_tool(runtime: ToolRuntime) -> str:
    """Return interests for the current student user.

    Wraps `database_utils.get_student_interests` using `runtime.state["user_id"]`.

    Args:
        ToolRuntime runtime: Runtime state for the current tool call:
            Required key: `runtime.state["user_id"]` as a student ID.

    Returns:
        out (str): JSON-encoded list of interests:
            Format of list items: Interest string as stored in `Interests.Interest` (e.g. "Artificial Intelligence").
            Note: If no interests are found, serialized value is ["No interests specified"].
    """
    with __connect() as conn:
        cursor = conn.cursor()
        try:
            interests = database_utils.get_student_interests(cursor, runtime.state["user_id"])
            return json.dumps(interests)
        except Exception as e:
            ERROR_LOG_FILE_PATH = _get_error_log_path()
            if not os.path.exists(ERROR_LOG_FILE_PATH):
                with open(ERROR_LOG_FILE_PATH, "w") as f:
                    f.write(f"Error log for {START_TIMESTAMP}\n\n")
            with open(ERROR_LOG_FILE_PATH, "a") as f:
                current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{current_timestamp}] Error occurred while fetching student interests: {e}\n")
            return "A problem occurred. End your task early and report the issue to the planning agent."

@tool("student_tracked_sections", description="Tool for getting the sections a student is currently tracking. The output is a list of tracked sections.", return_direct=True)
def get_student_tracked_sections_tool(runtime: ToolRuntime) -> str:
    """Return tracked sections for the current student user.

    Wraps `database_utils.get_student_tracked_sections` using `runtime.state["user_id"]`.

    Args:
        runtime (ToolRuntime): Runtime state for the current tool call:
            Required key: `runtime.state["user_id"]` as a student ID.

    Returns:
        out (str): JSON-encoded list of tracked section entries:
            Format: List[{
                "CourseCode": str,
                    Format: Department and course number as stored in `Courses.Department` and `Courses.Code` columns (e.g. "HST 210")
                "SectionNumber": str,
                    Format: Section number as stored in `Sections.SectionNumber` column (e.g. "001")
                "Name": str
                    Format: Course name as stored in `Courses.Name` column (e.g. "World History Since 1500")
            }]
            Note: If no tracked sections are found, serialized value is ["No sections currently being tracked"].
    """
    with __connect() as conn:
        cursor = conn.cursor()
        try:
            tracked_sections = database_utils.get_student_tracked_sections(cursor, runtime.state["user_id"])
            return json.dumps(tracked_sections)
        except Exception as e:
            ERROR_LOG_FILE_PATH = _get_error_log_path()
            if not os.path.exists(ERROR_LOG_FILE_PATH):
                with open(ERROR_LOG_FILE_PATH, "w") as f:
                    f.write(f"Error log for {START_TIMESTAMP}\n\n")
            with open(ERROR_LOG_FILE_PATH, "a") as f:
                current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{current_timestamp}] Error occurred while fetching student tracked sections: {e}\n")
            return "A problem occurred. End your task early and report the issue to the planning agent."

@tool("program_requirements", description="Tool for getting the course requirements for a specific program. The input is the program name and the output is a list of required courses.", return_direct=True)
def get_program_requirements_tool(program_name: str) -> str:
    """Return requirement strings for a program identified by title.

    Wraps `database_utils.get_program_requirements_by_title`.

    Args:
        program_name (str): Program title to look up:
            Format: Exact title as stored in `ProgramsOfStudy.Title` column (e.g. "Computer Information Systems").

    Returns:
        out (str): JSON-encoded list of requirement strings:
            Format of list items: Requirement string with one or more options joined by " OR ".
                Format for course options: "Department: {Department}, Course Number: {Code}, Title: {Name}"
                Format for elective options: "Any {Elective} course"
            Note: If no program is found, serialized value is ["Program not found"].
            Note: If found but no requirements exist, serialized value is ["No requirements found"].

    Warnings:
        Avoid high-volume program lookups in one call because payload size can become large. It should be used primarily for questions about course planning or if the user is curious about a specific program.
    """
    with __connect() as conn:
        cursor = conn.cursor()
        try:
            program_requirements = database_utils.get_program_requirements_by_title(cursor, program_name)
            return json.dumps(program_requirements)
        except Exception as e:
            ERROR_LOG_FILE_PATH = _get_error_log_path()
            if not os.path.exists(ERROR_LOG_FILE_PATH):
                with open(ERROR_LOG_FILE_PATH, "w") as f:
                    f.write(f"Error log for {START_TIMESTAMP}\n\n")
            with open(ERROR_LOG_FILE_PATH, "a") as f:
                current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{current_timestamp}] Error occurred while fetching program requirements: {e}\n")
            return "A problem occurred. End your task early and report the issue to the planning agent."

@tool("upcoming_events", description="Tool for getting a list of upcoming events. The output is a list of upcoming events with their names and descriptions.", return_direct=True)
def get_upcoming_events_tool() -> str:
    """Return upcoming events that have at least one future date.

    Wraps `database_utils.get_upcoming_events`.

    Returns:
        out (str): JSON-encoded list of upcoming events:
            Format: List[{
                "ID": str,
                    Format: Primary key value from `Events.ID` column (eg. "54321")
                "Name": str,
                    Format: Event name as stored in `Events.Name` column (e.g. "Spring Career Fair")
                "Description": str
                    Format: Event description as stored in `Events.Description` column (e.g. "An event where students can meet with potential employers and learn about job opportunities.")
            }]
    """
    with __connect() as conn:
        cursor = conn.cursor()
        try:
            upcoming_events = database_utils.get_upcoming_events(cursor)
            return json.dumps(upcoming_events)
        except Exception as e:
            ERROR_LOG_FILE_PATH = _get_error_log_path()
            if not os.path.exists(ERROR_LOG_FILE_PATH):
                with open(ERROR_LOG_FILE_PATH, "w") as f:
                    f.write(f"Error log for {START_TIMESTAMP}\n\n")
            with open(ERROR_LOG_FILE_PATH, "a") as f:
                current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{current_timestamp}] Error occurred while fetching upcoming events: {e}\n")
            return "A problem occurred. End your task early and report the issue to the planning agent."

@tool("event_dates", description="Tool for getting the dates for a specific event. The input is the event name and the output is a list of dates and their locations for that event.", return_direct=True)
def get_event_dates_tool(event_name: str) -> str:
    """Return future dates for a specific event identified by name.

    Wraps `database_utils.get_event_dates_by_name`.

    Args:
        event_name (str): Event name to look up:
            Format: Exact event name as stored in `Events.Name` column (e.g. "Spring Career Fair").

    Returns:
        out (str): JSON-encoded list of event date entries:
            Format: List[{
                "Date": str,
                    Format: Date of the event in YYYY-MM-DD format (e.g. "2024-04-15")
                "StartTime": str,
                    Format: Start time in 24-hour format (e.g. "13:00" for 1 PM)
                "EndTime": str,
                    Format: End time in 24-hour format (e.g. "14:15" for 2:15 PM)
                "Location": str
                    Format: Location string as stored in `EventDates.Location` column (e.g. "Building A Room 101", "Online")
            }]
            Note: If no event is found with the provided name, serialized value is ["Event not found"].
            Note: If the event exists but has no future dates, serialized value is [].
    """
    with __connect() as conn:
        cursor = conn.cursor()
        try:
            event_dates = database_utils.get_event_dates_by_name(cursor, event_name)
            return json.dumps(event_dates)
        except Exception as e:
            ERROR_LOG_FILE_PATH = _get_error_log_path()
            if not os.path.exists(ERROR_LOG_FILE_PATH):
                with open(ERROR_LOG_FILE_PATH, "w") as f:
                    f.write(f"Error log for {START_TIMESTAMP}\n\n")
            with open(ERROR_LOG_FILE_PATH, "a") as f:
                current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{current_timestamp}] Error occurred while fetching event dates: {e}\n")
            return "A problem occurred. End your task early and report the issue to the planning agent."

@tool("web_search", description="Tool for performing web searches. The input is a search query and the maximum number of results to return. The output is a list of search results with sources.", return_direct=True)
def web_search_tool(query: str, max_results: int = 5) -> str:
    """Performs a web search for the given query and return a list of results.

    Args:
        query (str): The search query.
        max_results (int): The maximum number of results to return.

    Returns:
        out (str): A string containing a list of search results:
            Format: List[{
                "Title": str,
                    Format: Title of the search result as returned by the search engine.
                "Link": str,
                    Format: URL of the search result as returned by the search engine.
                "Snippet": str
                    Format: A brief snippet of text from the search result as returned by the search engine.
            }]
    
    Warnings:
        Don't set the max_results parameter too high as it can consume a lot of tokens.
    """
    try:
        wrapper = DuckDuckGoSearchAPIWrapper(region="us-en", time="d", max_results=max_results)
        search = DuckDuckGoSearchResults(wrapper=wrapper, output_format="list")
        return search.invoke(query)
    except Exception as e:
        ERROR_LOG_FILE_PATH = _get_error_log_path()
        if not os.path.exists(ERROR_LOG_FILE_PATH):
            with open(ERROR_LOG_FILE_PATH, "w") as f:
                f.write(f"Error log for {START_TIMESTAMP}\n\n")
        with open(ERROR_LOG_FILE_PATH, "a") as f:
            current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{current_timestamp}] Error occurred while performing web search: {e}\n")
        return "A problem occurred. End your task early and report the issue to the planning agent."

@tool("get_web_page_content", description="Tool for getting the text content of a web page. The input is the URL of the web page and the maximum number of characters to return. The output is a string containing the text content of the web page. Use this tool sparingly as it can consume a lot of tokens.", return_direct=True)
def get_web_page_content_tool(url: str, max_chars: int = 3000) -> str:
    """Fetches the content of a web page and return it as text.

    Args:
        url (str): The URL of the web page to get the content from:
            Format: Valid URL string (e.g. "https://www.example.com").
        max_chars (int): The maximum number of characters to return:
            Format: Positive integer (e.g. 3000).
    
    Returns:
        out (str): A string containing the text content of the web page:
            Format: Text content of the web page with all HTML tags removed.

    Warnings:
        Use this tool sparingly as it can consume a lot of tokens, especially for if max_chars is set to a high value. Only use this tool if you are confident that the information you need is available on the page.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        ERROR_LOG_FILE_PATH = _get_error_log_path()
        if not os.path.exists(ERROR_LOG_FILE_PATH):
            with open(ERROR_LOG_FILE_PATH, "w") as f:
                f.write(f"Error log for {START_TIMESTAMP}\n\n")
        with open(ERROR_LOG_FILE_PATH, "a") as f:
            current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{current_timestamp}] Error occurred while fetching web page content from {url}: {e}\n")
        return f"Error fetching from {url}: {e}. The page may be unavailable or there may be a problem with the URL."
    try:
        soup = BeautifulSoup(response.text, 'html.parser')

        for script in soup(["script", "style, noscript"]):
            script.decompose()

        text = soup.get_text(separator=' ')
        text = ' '.join(text.split())
        if len(text) > max_chars:
            return text[:max_chars] + "... [truncated]"
        return text
    except Exception as e:
        ERROR_LOG_FILE_PATH = _get_error_log_path()
        if not os.path.exists(ERROR_LOG_FILE_PATH):
            with open(ERROR_LOG_FILE_PATH, "w") as f:
                f.write(f"Error log for {START_TIMESTAMP}\n\n")
        with open(ERROR_LOG_FILE_PATH, "a") as f:
            current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{current_timestamp}] Error occurred while parsing web page content from {url}: {e}\n")
        return f"Error parsing content from {url}: {e}. The page may be formatted in a way that is difficult to extract text from."

@tool("insert_student_interests", description="Tool for inserting a new interest for a student. The input is an interest to add, and the output is a confirmation message. Always check if a similar interest already exists in the database before adding it.", return_direct=True)
def insert_student_interests_tool(runtime: ToolRuntime, interest: str) -> str:
    """Insert an interest string for the current student user.

    Wraps `database_utils.insert_student_interests` with a single-item list input.

    Args:
        runtime (ToolRuntime): Runtime state for the current tool call:
            Required key: `runtime.state["user_id"]` as a student ID.
        interest (str): Interest string to be inserted:
            Format: Value to be stored in `Interests.Interest` column (e.g. "Data Science").

    Returns:
        out (str): Confirmation string from insert operation:
            Format: "{counter} new interest(s) added"

    Warnings:
        Always check for close duplicates before inserting to avoid duplicate interest rows.
    """
    with __connect() as conn:
        try:
            return database_utils.insert_student_interests(conn, runtime.state["user_id"], [interest])
        except Exception as e:
            ERROR_LOG_FILE_PATH = _get_error_log_path()
            if not os.path.exists(ERROR_LOG_FILE_PATH):
                with open(ERROR_LOG_FILE_PATH, "w") as f:
                    f.write(f"Error log for {START_TIMESTAMP}\n\n")
            with open(ERROR_LOG_FILE_PATH, "a") as f:
                current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{current_timestamp}] Error occurred while inserting student interests: {e}\n")
            return "A problem occurred. End your task early and report the issue to the planning agent."

@tool("insert_student_tracked_sections", description="Tool for inserting a new tracked section for a student. The input is the course code and section number for the section to track. The output is a confirmation message.", return_direct=True)
def insert_student_tracked_sections_tool(runtime: ToolRuntime, course_code: str, section_id: str) -> str:
    """Add a tracked section for the current student user.

    Wraps `database_utils.insert_student_tracked_section`.

    Args:
        runtime (ToolRuntime): Runtime state for the current tool call:
            Required key: `runtime.state["user_id"]` as a student ID.
        course_code (str): Course code of the section to track:
            Format: "DPT NUM" | "DPTNUM" (e.g. "CSC 101" or "CSC101").
        section_id (str): Section number to track:
            Format: Section number as stored in `Sections.SectionNum` (e.g. "1", "b1", "50").

    Returns:
        out (str): Confirmation string indicating result of the insert operation:
            Possible return values:
                "Section added to tracked sections"
                "Section not found"
                "Section already being tracked"
    """
    
    with __connect() as conn:
        try:
            return database_utils.insert_student_tracked_section(conn, runtime.state["user_id"], course_code, section_id)
        except Exception as e:
            ERROR_LOG_FILE_PATH = _get_error_log_path()
            if not os.path.exists(ERROR_LOG_FILE_PATH):
                with open(ERROR_LOG_FILE_PATH, "w") as f:
                    f.write(f"Error log for {START_TIMESTAMP}\n\n")
            with open(ERROR_LOG_FILE_PATH, "a") as f:
                current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{current_timestamp}] Error occurred while inserting student tracked sections: {e}\n")
            return "A problem occurred. End your task early and report the issue to the planning agent."

@tool("get_student_id_by_name", description="Tool for getting a student's ID based on their name. The input is the student's name and the output is the student's ID. Only works for students who have the current user as their advisor.", return_direct=True)
def get_student_id_by_name_tool(runtime: ToolRuntime, student_name: str) -> str:
    """Tool for getting a student's ID based on their name.

    Args:
        runtime (ToolRuntime): Runtime state for the current tool call:
            Required key: `runtime.state["user_id"]` as the advisor's parent user ID
        student_name (str): The name of the student to look up:
            Format: Exact name as stored in `Students.Name` column (e.g. "Alice Smith").
    
    Returns:
        out (str): The student's ID:
            Format: JSON-encoded dict {"Student ID": int} where the value is the primary key from `Students.ID` column (e.g. {"Student ID": 12345})
            Note: If no student with the given name is found or if the student does not have the current user as their advisor, returns "No student found with name {student_name}."

    Warnings:
        Name must be an exact match. If this fails to find the student, try using the get_advisor_students tool instead.
    """
    with __connect() as conn:
        cursor = conn.cursor()
        try:
            advisor_id = cursor.execute("SELECT ID FROM Advisors WHERE ParentID = ?", (runtime.state["user_id"],)).fetchone()
            if advisor_id is None:
                return f"No advisor found with user ID {runtime.state['user_id']}."
            cursor.execute("SELECT ID FROM Students WHERE name = ? and AdvisorID = ?", (student_name, advisor_id[0]))
            student_id = cursor.fetchone()
            if student_id:
                return json.dumps({"Student ID": student_id[0]})
            else:
                return f"No student found with name {student_name}."
        except Exception as e:
            ERROR_LOG_FILE_PATH = _get_error_log_path()
            current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(ERROR_LOG_FILE_PATH, "a") as f:
                f.write(f"[{current_timestamp}] Error occurred while getting student ID by name: {e}\n")
            return "A problem occurred. End your task early and report the issue to the planning agent."

@tool("get_advisor_students", description="Tool for getting a list of the students assigned to the current advisor. The output is a list of student names and their IDs.", return_direct=True)
def get_advisor_students_tool(runtime: ToolRuntime) -> str:
    """Return a list of students assigned to the current advisor.

    Args:
        runtime (ToolRuntime): Runtime state for the current tool call:
            Required key: `runtime.state["user_id"]` as the advisor's parent user ID.

    Returns:
        out (str): JSON-encoded list of students assigned to the current advisor:
            Format: List[{
                "name": str,
                    Format: Student name as stored in `Students.Name` column (e.g. "Alice Smith")
                "id": int
                    Format: Primary key value from `Students.ID` column (e.g. 12345)
            }]
        Note: If no students are found for the current advisor, returns a message indicating that no students were found.
    """
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
            ERROR_LOG_FILE_PATH = _get_error_log_path()
            if not os.path.exists(ERROR_LOG_FILE_PATH):
                with open(ERROR_LOG_FILE_PATH, "w") as f:
                    f.write(f"Error log for {START_TIMESTAMP}\n\n")
            with open(ERROR_LOG_FILE_PATH, "a") as f:
                current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{current_timestamp}] Error occurred while getting advisor students: {e}\n")
            return "A problem occurred. End your task early and report the issue to the planning agent."

@tool("student_basic_info", description="Tool for getting a student's basic information, including their name, GPA, total credits, and programs of study. The output is a string containing the relevant information. Only works for students who have the current user as their advisor.", return_direct=True)
def a_get_student_basic_info_tool(runtime: ToolRuntime, student_id: int) -> str:
    """Return basic profile information for an advisor-visible student.

    Performs advisor ownership checks, then wraps `database_utils.get_student_basic_info`.

    Args:
        runtime (ToolRuntime): Runtime state for the current tool call:
            Required key: `runtime.state["user_id"]` as the advisor's parent user ID.
        student_id (int): Student ID to retrieve:
            Format: Primary key value from `Students.ID` column (e.g. 12345).

    Returns:
        out (str): JSON-encoded student profile info:
            Format: {
                "Name": str,
                    Format: Student name as stored in `Students.Name` column (e.g. "Alice Smith")
                "Email": str,
                    Format: Student email as stored in `Students.Email` column (e.g. "alice@university.edu")
                "Advisor": str,
                    Format: Advisor name as stored in `Advisors.Name` column (e.g. "Dr. John Doe")
                "GPA": float,
                    Format: GPA value as stored in `Students.GPA` column (e.g. 3.75)
                "CreditsEarned": int,
                    Format: Total credits earned as stored in `Students.CreditsEarned` column (e.g. 90)
                "ProgramsOfStudy": list[dict]
                    Format of list items: {
                        "Title": str,
                            Format: Program title as stored in `ProgramsOfStudy.Title` column (e.g. "Computer Information Systems")
                        "Status": str
                            Format: Status string as stored in `StudentProgramsOfStudy.Status` column (e.g. "Declared", "In Progress", "Completed")
                    }
            }
            Access failure format: "Student with ID {student_id} is not assigned to the current user."
            Not-found format: "No student found with ID {student_id}"
    """
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
            ERROR_LOG_FILE_PATH = _get_error_log_path()
            if not os.path.exists(ERROR_LOG_FILE_PATH):
                with open(ERROR_LOG_FILE_PATH, "w") as f:
                    f.write(f"Error log for {START_TIMESTAMP}\n\n")
            with open(ERROR_LOG_FILE_PATH, "a") as f:
                current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{current_timestamp}] Error occurred while fetching student basic info: {e}\n")
            return "A problem occurred. End your task early and report the issue to the planning agent."

@tool("student_course_history", description="Tool for getting the course codes and titles for all courses a student has taken. The output is a list of courses taken. Only works for students who have the current user as their advisor.", return_direct=True)
def a_get_student_course_history_tool(runtime: ToolRuntime, student_id: int) -> str:
    """Return course history for an advisor-visible student.

    Performs advisor ownership checks, then wraps `database_utils.get_student_course_history`.

    Args:
        runtime (ToolRuntime): Runtime state for the current tool call:
            Required key: `runtime.state["user_id"]` as the advisor's parent user ID.
        student_id (int): Student ID to retrieve:
            Format: Primary key value from `Students.ID` column (e.g. 12345).

    Returns:
        out (str): JSON-encoded list of course-history entries:
            Format: List[{
                "CourseCode": str,
                    Format: Course code as stored in `Courses.Code` column (e.g. "CS101")
                "Name": str,
                    Format: Course name as stored in `Courses.Name` column (e.g. "Introduction to Computer Science")
                "Grade": str
                    Format: Grade string as stored in `StudentCourseHistory.Grade` column (e.g. "A", "B+", "Pass", "Fail")
            }]
            Note: If no courses are found, serialized value is ["No courses taken"].
            Access failure format: "Student with ID {student_id} is not assigned to the current user."
            Not-found format: "No student found with ID {student_id}"
    """
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
            ERROR_LOG_FILE_PATH = _get_error_log_path()
            if not os.path.exists(ERROR_LOG_FILE_PATH):
                with open(ERROR_LOG_FILE_PATH, "w") as f:
                    f.write(f"Error log for {START_TIMESTAMP}\n\n")
            with open(ERROR_LOG_FILE_PATH, "a") as f:
                current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{current_timestamp}] Error occurred while fetching student course history: {e}\n")
            return "A problem occurred. End your task early and report the issue to the planning agent."

@tool("student_interests", description="Tool for getting a student's interests. The output is a list of interests. Only works for students who have the current user as their advisor.", return_direct=True)
def a_get_student_interests_tool(runtime: ToolRuntime, student_id: int) -> str:
    """Return interests for an advisor-visible student.

    Performs advisor ownership checks, then wraps `database_utils.get_student_interests`.

    Args:
        runtime (ToolRuntime): Runtime state for the current tool call:
            Required key: `runtime.state["user_id"]` as the advisor's parent user ID.
        student_id (int): Student ID to retrieve:
            Format: Primary key value from `Students.ID` column (e.g. 12345).

    Returns:
        out (str): JSON-encoded list of interests:
            Format of list items: Interest string as stored in `Interests.Interest`.
            Note: If no interests are found, serialized value is ["No interests specified"].
            Access failure format: "Student with ID {student_id} is not assigned to the current user."
            Not-found format: "No student found with ID {student_id}"
    """
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
            ERROR_LOG_FILE_PATH = _get_error_log_path()
            if not os.path.exists(ERROR_LOG_FILE_PATH):
                with open(ERROR_LOG_FILE_PATH, "w") as f:
                    f.write(f"Error log for {START_TIMESTAMP}\n\n")
            with open(ERROR_LOG_FILE_PATH, "a") as f:
                current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{current_timestamp}] Error occurred while fetching student interests: {e}\n")
            return "A problem occurred. End your task early and report the issue to the planning agent."

@tool("student_tracked_sections", description="Tool for getting the sections a student is currently tracking. The output is a list of tracked sections. Only works for students who have the current user as their advisor.", return_direct=True)
def a_get_student_tracked_sections_tool(runtime: ToolRuntime, student_id: int) -> str:
    """Return tracked sections for an advisor-visible student.

    Performs advisor ownership checks, then wraps `database_utils.get_student_tracked_sections`.

    Args:
        runtime (ToolRuntime): Runtime state for the current tool call:
            Required key: `runtime.state["user_id"]` as the advisor's parent user ID.
        student_id (int): Student ID to retrieve:
            Format: Primary key value from `Students.ID` column (e.g. 12345).

    Returns:
        out (str): JSON-encoded list of tracked sections:
            Format: List[{
                "CourseCode": str,
                    Format: Course code as stored in `Courses.Code` column (e.g. "CS101")
                "SectionNumber": str,
                    Format: Section number as stored in `Sections.SectionNumber` column (e.g. "001")
                "Name": str,
                    Format: Section name as stored in `Sections.Name` column (e.g. "Introduction to Computer Science")
            }]
            Note: If no tracked sections are found, serialized value is ["No sections currently being tracked"].
            Access failure format: "Student with ID {student_id} is not assigned to the current user."
            Not-found format: "No student found with ID {student_id}"
    """
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
            ERROR_LOG_FILE_PATH = _get_error_log_path()
            if not os.path.exists(ERROR_LOG_FILE_PATH):
                with open(ERROR_LOG_FILE_PATH, "w") as f:
                    f.write(f"Error log for {START_TIMESTAMP}\n\n")
            with open(ERROR_LOG_FILE_PATH, "a") as f:
                current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{current_timestamp}] Error occurred while fetching student tracked sections: {e}\n")
            return "A problem occurred. End your task early and report the issue to the planning agent."

d_tools = [get_current_time_tool if TOOL_CONFIG["s-db-tools"]["get_current_time_tool"] else None,
           get_department_list_tool if TOOL_CONFIG["s-db-tools"]["get_department_list_tool"] else None,
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
            get_department_list_tool if TOOL_CONFIG["a-db-tools"]["get_department_list_tool"] else None,
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
