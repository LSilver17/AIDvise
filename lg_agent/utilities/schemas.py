from pydantic import BaseModel, Field

class AdvisorOutputSchema(BaseModel):
    """Schema for the output of the advisor node, which indicates whether a database query or web search is needed, and provides an answer if not."""

    requires_database: bool = Field(description="Indicates if a database query is required to answer the question. The database contains information about the courses offered at the student's college, including course requirements, sections, and meet times.")
    requires_web_search: bool = Field(description="Indicates if a web search is required to answer the question.")
    answer: str = Field(description="The answer to the user's question, if it can be provided without additional information. Should be left blank if either of the first two fields are true. Keep responses clear and concise.")
    info_needed_db: str = Field(description="If the advisor cannot answer the question directly, this field should specify what information from the database is needed to answer the question. If requires_database is false, leave this field blank.")
    info_needed_web: str = Field(description="If the advisor cannot answer the question directly, this field should specify what information from the web is needed to answer the question. If requires_web_search is false, leave this field blank.")