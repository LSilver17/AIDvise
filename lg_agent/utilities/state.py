from typing_extensions import TypedDict, Literal
from typing import Annotated
from operator import add
from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
import sqlite3

class AdvisorState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    plan: dict
    db_info: dict
    web_info: dict
    sqlite_cursor: sqlite3.Cursor
    num_messages: int