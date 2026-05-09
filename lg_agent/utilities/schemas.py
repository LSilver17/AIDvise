"""
Copyright 2026 Luca Silver

Provides pydantic schemas for the advisor graph and alerts graph.

Plan Schemas:
- SPlanSchema: Schema for the advisor planning node used by student users. Determines whether database queries, web searches, or database insertions are needed to answer a student's question, and specifies what information is needed from each source if applicable. The schema structure varies based on the context selection in context_config.json, with different fields included for 'full', 'some-db', 'no-db', and 'no-tools' modes.
- APlanSchema: Schema for the advisor planning node used by advisor users. Similar to SPlanSchema but does not include the database insertion field. The structure also varies based on context selection in context_config.json.

Filter Schemas:
- DBTerm: Represents an academic term (year, season, and optional number for split sessions). Used for filtering courses and sections by term.
- DBMeetTime: Represents the meeting times for course sections (days of the week and start/end times). Used for filtering sections by schedule.
- CreditCondition: Represents a filter condition for course credits, allowing comparison operators (e.g., '=', '>=', etc.) to specify credit requirements in course filters.
- EnrollmentCondition: Represents a filter condition for section enrollment, allowing comparison operators to specify enrollment thresholds in section filters.
- CodeCondition: Represents a filter condition for course codes, allowing comparison operators to specify course number requirements in course filters.
- CourseFilters: Comprehensive filter schema for querying courses from the database, including filters for term, department, course code, credits, keywords, and prerequisites.
- SectionFilters: Comprehensive filter schema for querying course sections from the database, including filters for term, course code, instructor, teaching method, enrollment capacity, current enrollment, location, and meeting times.

Alert Schemas:
- RelevantEventsObject: Represents an individual event with its ID and urgency level.
- RelevantEventsSchema: Schema for returning a list of relevant events with their urgency levels.

Single line comments are used in place of docstrings to save on tokens, but detailed descriptions are provided in the field definitions for clarity on the purpose and usage of each field within the schemas.
"""

import sys, os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from pydantic import BaseModel, Field
import json

CONTEXT_CONFIG_PATH = os.path.join(ROOT_DIR, "context_config.json")

with open(CONTEXT_CONFIG_PATH, "r") as f:
    CONTEXT_CONFIG = json.load(f)

# Schemas for advisor graph

if CONTEXT_CONFIG["s-planner"]["context-select"] == "full":
    class SPlanSchema(BaseModel):
        # Planning schema for student advisor chat - full context mode.
        # Determines whether external information sources (database, web) are needed to answer
        # a student's question. Used by the student planning node to route questions to appropriate
        # retrieval tools or provide direct answers when possible.
        # In 'full' mode, supports database queries for student-specific data, web searches,
        # and insertion of new student interests/course preferences.

        requires_database: bool = Field(default=False, description="Indicates if a more database queries are required to answer the question. The database contains information about the courses offered at the student's college, including course requirements, sections, and meet times. It also has information about the student, including their academic history and their interests.")
        requires_web_search: bool = Field(default=False, description="Indicates if a web search is required to answer the question. If information is needed from both the database and the web, both fields should be set to true.")
        requires_insertion: bool = Field(default=False, description="Indicates if the advisor needs to insert information into the database. This should be used if the student mentions interests of their's or course sections they are interested in.")
        answer: str = Field(default="", description="The answer to the user's question, if it can be provided without additional information. Should be left blank if either of the first two fields are true. Keep responses clear and concise.")
        info_needed_db: str = Field(default=None, description="If the advisor cannot answer the question directly, this field should specify what information from the database is needed to answer the question. If no info is needed leave this field blank.")
        info_needed_web: str = Field(default=None, description="If the advisor cannot answer the question directly, this field should specify what information from the web is needed to answer the question. If no info is needed leave this field blank.")
        info_to_insert: str = Field(default=None, description="If the advisor needs to insert information into the database, this field should specify what information needs to be inserted. If no insertion is needed, leave this field blank.")

elif CONTEXT_CONFIG["s-planner"]["context-select"] == "some-db":
    class SPlanSchema(BaseModel):
        # Planning schema for student advisor chat - limited database access mode.
        # Determines whether external information sources (database, web) are needed to answer
        # a student's question. Used by the student planning node to route questions appropriately.
        # In 'some-db' mode, database queries are limited to course/program information only,
        # without access to individual student data. Web searches are still supported.

        requires_database: bool = Field(default=False, description="Indicates if a more database queries are required to answer the question. The database contains information about the courses offered at the student's college, including course requirements, sections, and meet times.")
        requires_web_search: bool = Field(default=False, description="Indicates if a web search is required to answer the question. If information is needed from both the database and the web, both fields should be set to true.")
        answer: str = Field(default="", description="The answer to the user's question, if it can be provided without additional information. Should be left blank if either of the first two fields are true. Keep responses clear and concise.")
        info_needed_db: str = Field(default=None, description="If the advisor cannot answer the question directly, this field should specify what information from the database is needed to answer the question. If no info is needed leave this field blank.")
        info_needed_web: str = Field(default=None, description="If the advisor cannot answer the question directly, this field should specify what information from the web is needed to answer the question. If no info is needed leave this field blank.")

elif CONTEXT_CONFIG["s-planner"]["context-select"] == "no-db":
    class SPlanSchema(BaseModel):
        # Planning schema for student advisor chat - web-only mode.
        # Determines whether a web search is needed to answer a student's question.
        # Used by the student planning node when database access is disabled.
        # In 'no-db' mode, only web searches and direct answers are available;
        # no database queries are performed.

        requires_web_search: bool = Field(default=False, description="Indicates if a web search is required to answer the question.")
        answer: str = Field(default="", description="The answer to the user's question, if it can be provided without additional information. Should be left blank if the prior field is true. Keep responses clear and concise.")
        info_needed_web: str = Field(default=None, description="If the advisor cannot answer the question directly, this field should specify what information from the web is needed to answer the question. If no info is needed leave this field blank.")

elif CONTEXT_CONFIG["s-planner"]["context-select"] == "no-tools":
    class SPlanSchema(BaseModel):
        # Planning schema for student advisor chat - no external tools mode.
        # Minimal schema that only provides a direct answer to the student's question.
        # Used when all external tools (database, web search) are disabled.
        # In 'no-tools' mode, the advisor responds based on context and general knowledge only.

        answer: str = Field(default="", description="The answer to the user's question. Keep responses clear and concise.")

else:
    raise ValueError("Invalid context select value in context_config.json. Must be one of 'full', 'no-db', or 'no-tools'.")

if CONTEXT_CONFIG["a-planner"]["context-select"] == "full":
    class APlanSchema(BaseModel):
        # Planning schema for admin advisor chat - full context mode.
        # Determines whether external information sources (database, web) are needed to answer
        # an admin's question. Used by the admin planning node to route questions to appropriate
        # retrieval tools or provide direct answers when possible.
        # In 'full' mode, supports database queries for administrative data (courses, programs,
        # sections, student info) and web searches.

        requires_database: bool = Field(description="Indicates if a more database queries are required to answer the question. The database contains information about the courses offered at the student's college, including course requirements, sections, and meet times. It also has information about the student, including their academic history and their interests.")
        requires_web_search: bool = Field(description="Indicates if a web search is required to answer the question. If information is needed from both the database and the web, both fields should be set to true.")
        answer: str = Field(default="", description="The answer to the user's question, if it can be provided without additional information. Should be left blank if either of the first two fields are true. Keep responses clear and concise.")
        info_needed_db: str = Field(default=None, description="If the advisor cannot answer the question directly, this field should specify what information from the database is needed to answer the question. If no info is needed leave this field blank.")
        info_needed_web: str = Field(default=None, description="If the advisor cannot answer the question directly, this field should specify what information from the web is needed to answer the question. If no info is needed leave this field blank.")

elif CONTEXT_CONFIG["a-planner"]["context-select"] == "some-db":
    class APlanSchema(BaseModel):
        # Planning schema for admin advisor chat - limited database access mode.
        # Determines whether external information sources (database, web) are needed to answer
        # an admin's question. Used by the admin planning node to route questions appropriately.
        # In 'some-db' mode, database queries are restricted to course/program information only,
        # without full administrative access. Web searches are still supported.

        requires_database: bool = Field(default=False, description="Indicates if a more database queries are required to answer the question. The database contains information about the courses offered at the student's college, including course requirements, sections, and meet times.")
        requires_web_search: bool = Field(default=False, description="Indicates if a web search is required to answer the question. If information is needed from both the database and the web, both fields should be set to true.")
        answer: str = Field(default="", description="The answer to the user's question, if it can be provided without additional information. Should be left blank if either of the first two fields are true. Keep responses clear and concise.")
        info_needed_db: str = Field(default=None, description="If the advisor cannot answer the question directly, this field should specify what information from the database is needed to answer the question. If no info is needed leave this field blank.")
        info_needed_web: str = Field(default=None, description="If the advisor cannot answer the question directly, this field should specify what information from the web is needed to answer the question. If no info is needed leave this field blank.")

elif CONTEXT_CONFIG["a-planner"]["context-select"] == "no-db":
    class APlanSchema(BaseModel):
        # Planning schema for admin advisor chat - web-only mode.
        # Determines whether a web search is needed to answer an admin's question.
        # Used by the admin planning node when database access is disabled.
        # In 'no-db' mode, only web searches and direct answers are available;
        # no database queries are performed.

        requires_web_search: bool = Field(default=False, description="Indicates if a web search is required to answer the question.")
        answer: str = Field(default="", description="The answer to the user's question, if it can be provided without additional information. Should be left blank if the prior field is true. Keep responses clear and concise.")
        info_needed_web: str = Field(default=None, description="If the advisor cannot answer the question directly, this field should specify what information from the web is needed to answer the question. If no info is needed leave this field blank.")

elif CONTEXT_CONFIG["a-planner"]["context-select"] == "no-tools":
    class APlanSchema(BaseModel):
        # Planning schema for admin advisor chat - no external tools mode.
        # Minimal schema that only provides a direct answer to the admin's question.
        # Used when all external tools (database, web search) are disabled.
        # In 'no-tools' mode, the advisor responds based on context and general knowledge only.

        answer: str = Field(default="", description="The answer to the user's question. Keep responses clear and concise.")

else:
    print(CONTEXT_CONFIG["a-planner"]["context-select"])
    raise ValueError("Invalid context select value in context_config.json. Must be one of 'full', 'no-db', or 'no-tools'.")

class DBTerm(BaseModel):
    # Represents a single academic term or session.
    # Used throughout the system to filter and organize courses, sections, and student
    # records by academic period. Supports split sessions (e.g., Fall 1 and Fall 2).
    # Examples:
    #   - {"year": 2024, "season": "Fall", "number": None}
    #   - {"year": 2024, "season": "Summer", "number": 1}

    year: int = Field(description="The year of the term (e.g. 2023)")
    season: str = Field(description="The season of the term (e.g. Fall, Spring, Summer)")
    number: int = Field(default=None, description="If the season is split in two halves, this field indicates which half it is (e.g. 1 for Fall 1, 2 for Fall 2, etc.). If the season is not split, this field should be set to none.")

class DBMeetTime(BaseModel):
    # Represents the schedule/time slot for a course section meeting.
    # Used to store and filter course sections by when they meet. Supports multiple
    # meeting times per section (e.g., MW 10:00-11:15 and F 10:00-11:15).
    # Times are stored in 24-hour format for consistency and comparison operations.
    # Examples:
    #   - {"days": "MW", "start_time": "10:00", "end_time": "11:15"}
    #   - {"days": "TR", "start_time": "14:00", "end_time": "15:15"}

    days: str = Field(description="The days of the week the section meets (e.g. MW, TR, F, etc.)")
    start_time: str = Field(description="The start time of the section in 24-hour format (e.g. 14:00)")
    end_time: str = Field(description="The end time of the section in 24-hour format (e.g. 15:15)")

class CreditCondition(BaseModel):
    # Filter condition for querying courses by credit hours.
    # Allows flexible credit-based filtering using comparison operators.
    # Used in CourseFilters to find courses matching specific credit requirements.
    # Examples:
    #   - {"condition": "=", "credits": 3}  # Find 3-credit courses
    #   - {"condition": ">=", "credits": 3}  # Find courses worth 3+ credits

    condition: str = Field(description="The condition to apply to the number of credits ['=' | '>' | '<' | '>=' | '<=' | '!=']")
    credits: int = Field(description="Number of credits to compare against.")

class EnrollmentCondition(BaseModel):
    # Filter condition for querying sections by enrollment status.
    # Allows flexible enrollment-based filtering using comparison operators.
    # Can filter by enrollment capacity or current enrollment in SectionFilters.
    # Examples:
    #   - {"condition": "<", "enrollment": 30}  # Find sections with < 30 enrolled
    #   - {"condition": "=", "enrollment": 0}   # Find completely empty sections

    condition: str = Field(description="The condition to apply to the enrollment status ['=' | '>' | '<' | '>=' | '<=' | '!=']")
    enrollment: int = Field(description="Enrollment number to compare against.")

class CodeCondition(BaseModel):
    # Filter condition for querying courses by course number/code.
    # Allows flexible course code filtering using comparison operators.
    # Used in CourseFilters to find courses within specific numbering ranges.
    # Examples:
    #   - {"condition": ">=", "code": "100"}  # Find 100-level or higher courses
    #   - {"condition": "<", "code": "500"}   # Find courses below 500-level

    condition: str = Field(description="The condition to apply to the course code ['=' | '!=' | '>' | '<' | '>=' | '<=']")
    code: str = Field(description="Course number to compare against (e.g. '101')")
class CourseFilters(BaseModel):
    # Comprehensive filter set for querying courses from the database.
    # Enables multi-dimensional filtering of courses by academic term, department,
    # course level, credit hours, content, and prerequisites. All filter fields are
    # optional; only specified filters are applied during queries.
    # Fields are combined with AND logic - a course must match all provided filters.
    # Typical usage:
    #   - Filter courses by department and term
    #   - Find courses by keyword and credit requirement
    #   - Search for prerequisites in course descriptions

    terms: list[DBTerm] = Field(default=[], description="List of terms to filter courses by. Each term should be specified as a year, season, and, if applicable, number (2023, 'Fall', None; 2023, 'Summer', 1, etc). If no term filter is needed, leave this field blank.")
    departments: list[str] = Field(default=[], description="List of departments to filter courses by (e.g. ['CSCI', 'MATH']). If no department filter is needed, leave this field blank.")
    course_codes: list[CodeCondition] = Field(default=[], description="List of course code conditions to filter courses by. Each condition should specify a comparison condition and a course number to compare against (e.g. [{'condition': '>=', 'code': '100'}] to filter for courses with a number greater than or equal to 100). If no course code filter is needed, leave this field blank.")
    credits: list[CreditCondition] = Field(default=[], description="Filter courses by number of credits. If no credit filter is needed, leave this field blank.")
    keywords: list[str] = Field(default=[], description="List of keywords to search for in course descriptions. If no keyword filter is needed, leave this field blank.")
    prerequisites: list[str] = Field(default=[], description="List of keywords to search for in course prerequisites. If searching for a course use its code rather than its title. If no prerequisite filter is needed, leave this field blank.")

class SectionFilters(BaseModel):
    # Comprehensive filter set for querying course sections from the database.
    # Enables multi-dimensional filtering of course sections by academic term, course code,
    # instructor, teaching method, enrollment (capacity and current), location, and meeting times.
    # All filter fields are optional; only specified filters are applied during queries.
    # Fields are combined with AND logic - a section must match all provided filters.
    # Typical usage:
    #   - Find available sections of a specific course
    #   - Filter sections by instructor preference
    #   - Find sections meeting at specific times or locations
    #   - Identify sections with open enrollment capacity

    terms: list[DBTerm] = Field(default=[], description="List of terms to filter sections by, specified as a year, season, and, if applicable, number (2023, 'Fall', None; 2023, 'Summer', 1, etc). If no term filter is needed, leave this field blank.")
    course_codes: list[str] = Field(default=[], description="List of course codes to filter sections by (e.g. ['CSCI 101', 'MATH 101']). If no course code filter is needed, leave this field blank.")
    instructors: list[str] = Field(default=[], description="List of instructors to filter sections by (e.g. ['John Doe', 'Jane Smith']). If no instructor filter is needed, leave this field blank.")
    teaching_methods: list[str] = Field(default=[], description="List of teaching methods to filter sections by (e.g. ['Lecture', 'Lab', 'Online']). If no teaching method filter is needed, leave this field blank.")
    enrollment_capacity: list[EnrollmentCondition] = Field(default=[], description="Filter sections by enrollment capacity. If no enrollment filter is needed, leave this field blank.")
    enrollment: list[EnrollmentCondition] = Field(default=[], description="Filter sections by current enrollment. If no enrollment filter is needed, leave this field blank.")
    locations: list[str] = Field(default=[], description="List of locations to filter sections by (e.g. ['Building A Room 101', 'Online']). If no location filter is needed, leave this field blank.")
    meet_times: list[DBMeetTime] = Field(default=[], description="List of meet times to filter sections by. If no meet time filter is needed, leave this field blank.")

# Schemas for alerts graph

class RelevantEventsObject(BaseModel):
    # Individual event with priority information for alert generation.
    # Used to identify and prioritize important events in a student's academic calendar
    # that may warrant notifications or advisor alerts.
    ID: int = Field(description="The unique identifier for the event (not the event date).")
    Urgency: int = Field(description="The urgency level of the event, based on how much time/effort it may require and how much time is left before the event occurs. Range should be from 1 to 5, with 5 being the most urgent.")

class RelevantEventsSchema(BaseModel):
    # Alert schema containing a prioritized list of relevant events.
    # Used by the alert generation node to return identified events that may warrant
    # notifications. Events are pre-sorted by urgency level, with the most urgent
    # events having higher priority for notification.
    # Note: Field name contains typo 'relivent_events' (should be 'relevant_events')
    # maintained for backward compatibility.
    relivent_events: list[RelevantEventsObject] = Field(description="A list of relevant events, each with its ID and urgency level.")
