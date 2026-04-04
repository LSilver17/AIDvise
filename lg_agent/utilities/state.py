from typing_extensions import TypedDict
from typing import Annotated
from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages

class QueryResult(TypedDict):
    query: str
    result: str

class AdvisorInput(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

class AdvisorState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    db_info: list[QueryResult]
    web_info: list[QueryResult]
    plan: dict

class DatabaseHelperState(TypedDict):
    info_needed: str

class DatabaseHelperOutput(TypedDict):
    info: QueryResult

class WebSearchHelperState(TypedDict):
    info_needed: str

class WebSearchHelperOutput(TypedDict):
    info: QueryResult
