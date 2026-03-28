from typing_extensions import TypedDict
from typing import Annotated
from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from datetime import datetime
from utilities.schemas import RelevantEventsSchema

# States for the AdvisorAgent

class AdvisorState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
<<<<<<< HEAD
    db_info: list[QueryResult]
    web_info: list[QueryResult]
    plan: dict
    loop_count: int

class DatabaseHelperState(TypedDict):
    info_needed: str
    messages: Annotated[list[AnyMessage], add_messages]
    loop_count: int

class DatabaseHelperOutput(TypedDict):
    info: QueryResult

class WebSearchHelperState(TypedDict):
    info_needed: str
    messages: Annotated[list[AnyMessage], add_messages]
    loop_count: int

class WebSearchHelperOutput(TypedDict):
    info: QueryResult
=======
    num_messages: int = 0

# States for the AlertsAgent

class AlertsAgentInput(TypedDict):
    student_id: int

class AlertsAgentState(TypedDict):
    student_id: int
    upcoming_events: list[dict]
    student_interests: list[str]
    relevant_events: list[RelevantEventsSchema]

class AlertsAgentOutput(TypedDict):
    relevant_events: list[RelevantEventsSchema]