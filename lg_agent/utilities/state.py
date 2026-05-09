"""
Copyright 2026 Luca Silver

Defines TypedDict schemas for state management across the advisor and alerts LangGraph agents.

Planner Agent State Classes:
- `QueryResult`: Container for database/web query strings and their results.
- `RouteState`: Root routing state containing user ID, account type, and messages.
- `SPlannerState`: State for student planning node, tracking database/web info and loop iterations.
- `APlannerState`: State for advisor planning node, similar to student but without insertion field.
- `DatabaseHelperState`: State for database query helper subgraph.
- `DatabaseHelperOutput`: Output schema for database helper results.
- `WebSearchHelperState`: State for web search helper subgraph.
- `WebSearchHelperOutput`: Output schema for web search helper results.
- `InsertionHelperState`: State for student insertion helper subgraph.
- `InsertionHelperOutput`: Output schema for insertion helper results.

Alerts Agent State Classes:
- `AlertsAgentInput`: Input schema containing the student ID to process.
- `AlertsAgentState`: State containing upcoming events, interests, and relevant filtered events.
- `AlertsAgentOutput`: Output schema containing the final list of relevant events.
"""

import sys, os
    
# adds utilities directory to system path if not already there
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from langchain.messages import AIMessage
from typing_extensions import Literal, TypedDict
from typing_extensions import TypedDict
from typing import Annotated, NotRequired
from langchain_core.messages import AnyMessage
from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from utilities.schemas import RelevantEventsSchema

# States for the PlannerAgent

class QueryResult(TypedDict):
    query: str
    result: str

class RouteState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    user_id: int
    account_type: Literal["Student", "Advisor"]

class SPlannerState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    db_info: NotRequired[list[QueryResult]]
    web_info: NotRequired[list[QueryResult]]
    insertion_result: str
    plan: dict
    loop_count: int
    user_id: int

class APlannerState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    db_info: NotRequired[list[QueryResult]]
    web_info: NotRequired[list[QueryResult]]
    plan: dict
    loop_count: int
    user_id: int

class DatabaseHelperState(TypedDict):
    info_needed: str
    messages: Annotated[list[AnyMessage], add_messages]
    loop_count: int
    user_id: int
    account_type: Literal["Student", "Advisor"]

class DatabaseHelperOutput(TypedDict):
    info: QueryResult

class WebSearchHelperState(TypedDict):
    info_needed: str
    messages: Annotated[list[AnyMessage], add_messages]
    loop_count: int

class WebSearchHelperOutput(TypedDict):
    info: QueryResult

class InsertionHelperState(TypedDict):
    info_to_insert: str
    messages: Annotated[list[AnyMessage], add_messages]
    loop_count: int
    user_id: int

class InsertionHelperOutput(TypedDict):
    result: str

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