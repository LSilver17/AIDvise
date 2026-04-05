from langchain_core.messages import AIMessage
from pydantic.dataclasses import dataclass
from typing_extensions import TypedDict
from typing import Annotated
from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages

class QueryResult(TypedDict):
    query: str
    result: AIMessage

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
