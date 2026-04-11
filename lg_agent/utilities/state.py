import sys, os
    
# adds utilities directory to system path if not already there
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from langchain.messages import AIMessage
from typing_extensions import TypedDict
from typing_extensions import TypedDict
from typing import Annotated
from langchain_core.messages import AnyMessage
from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from utilities.schemas import RelevantEventsSchema

# States for the AdvisorAgent

class QueryResult(TypedDict):
    query: str
    result: str

class AdvisorState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
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