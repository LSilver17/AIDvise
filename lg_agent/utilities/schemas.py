from pydantic import BaseModel, Field

# Schemas for advisor graph
class PlanSchema(BaseModel):
    """Schema for the output of the advisor node, which indicates whether a database query or web search is needed, and provides an answer if not."""

    requires_database: bool = Field(description="Indicates if a more database queries are required to answer the question. The database contains information about the courses offered at the student's college, including course requirements, sections, and meet times.")
    requires_web_search: bool = Field(description="Indicates if a web search is required to answer the question. If information is needed from both the database and the web, both fields should be set to true.")
    answer: str = Field(description="The answer to the user's question, if it can be provided without additional information. Should be left blank if either of the first two fields are true. Keep responses clear and concise.")
    info_needed_db: str = Field(description="If the advisor cannot answer the question directly, this field should specify what information from the database is needed to answer the question. If requires_database is false, leave this field blank.")
    info_needed_web: str = Field(description="If the advisor cannot answer the question directly, this field should specify what information from the web is needed to answer the question. If requires_web_search is false, leave this field blank.")

class DBTerm(BaseModel):
    """Schema for a term in the academic calendar."""

    year: int = Field(description="The year of the term (e.g. 2023)")
    season: str = Field(description="The season of the term (e.g. Fall, Spring, Summer)")
    number: int | None = Field(description="If the season is split in two halves, this field indicates which half it is (e.g. 1 for Fall 1, 2 for Fall 2, etc.). If the season is not split, this field should be set to none.")

class DBMeetTime(BaseModel):
    """Schema for a meet time of a course section."""

    days: str = Field(description="The days of the week the section meets (e.g. MW, TR, F, etc.)")
    start_time: str = Field(description="The start time of the section in 24-hour format (e.g. 14:00)")
    end_time: str = Field(description="The end time of the section in 24-hour format (e.g. 15:15)")

class CreditCondition(BaseModel):
    """Schema for a credit filter condition."""

    condition: str = Field(description="The condition to apply to the number of credits (e.g. '=', '>', '<', '>=', '<=', '!=')")
    credits: int = Field(description="Number of credits to compare against.")

class EnrollmentCondition(BaseModel):
    """Schema for an enrollment filter condition."""

    condition: str = Field(description="The condition to apply to the enrollment status (e.g. '=', '>', '<', '>=', '<=', '!=')")
    enrollment: int = Field(description="Enrollment number to compare against.")

class CourseFilters(BaseModel):
    """Schema for the filters that can be applied when querying for courses in the database."""

    terms: list[DBTerm] | None = Field(description="List of terms to filter courses by. Each term should be specified as a year, season, and, if applicable, number (2023, 'Fall', None; 2023, 'Summer', 1, etc). If no term filter is needed, leave this field blank.")
    departments: list[str] | None = Field(description="List of departments to filter courses by (e.g. ['CSCI', 'MATH']). If no department filter is needed, leave this field blank.")
    credits: CreditCondition | None = Field(description="Filter courses by number of credits. If no credit filter is needed, leave this field blank.")

class SectionFilters(BaseModel):
    """Schema for the filters that can be applied when querying for sections in the database."""

    terms: list[DBTerm] | None = Field(description="List of terms to filter sections by, specified as a year, season, and, if applicable, number (2023, 'Fall', None; 2023, 'Summer', 1, etc). If no term filter is needed, leave this field blank.")
    course_codes: list[str] | None = Field(description="List of course codes to filter sections by (e.g. ['CSCI 101', 'MATH 101']). If no course code filter is needed, leave this field blank.")
    instructors: list[str] | None = Field(description="List of instructors to filter sections by (e.g. ['John Doe', 'Jane Smith']). If no instructor filter is needed, leave this field blank.")
    teaching_methods: list[str] | None = Field(description="List of teaching methods to filter sections by (e.g. ['Lecture', 'Lab', 'Online']). If no teaching method filter is needed, leave this field blank.")
    enrollment_capacity: EnrollmentCondition | None = Field(description="Filter sections by enrollment capacity. If no enrollment filter is needed, leave this field blank.")
    enrollment: EnrollmentCondition | None = Field(description="Filter sections by current enrollment. If no enrollment filter is needed, leave this field blank.")
    locations: list[str] | None = Field(description="List of locations to filter sections by (e.g. ['Building A Room 101', 'Online']). If no location filter is needed, leave this field blank.")
    meet_times: list[DBMeetTime] | None = Field(description="List of meet times to filter sections by. If no meet time filter is needed, leave this field blank.")

# Schemas for alerts graph

class ReliventEventsObject(BaseModel):
    ID: int = Field(description="The unique identifier for the event."),
    UrgencyLevel: str = Field(description="The urgency level of the event, based on how much time/effort it may require and how much time is left before the event occurs.")

class RelevantEventsSchema(BaseModel):
    relivent_events: list[ReliventEventsObject] = Field(description="A list of relevant events, each with its ID and urgency level.")
