from typing_extensions import TypedDict, Literal
from typing import Annotated
from operator import add
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, AnyMessage
from langgraph.graph import add_messages

class AdvisorState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    num_calls: int