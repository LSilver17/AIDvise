from typing_extensions import TypedDict, Literal
from typing import Annotated
from operator import add
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, AnyMessage
from langgraph.graph import add_messages
from datetime import datetime

class AdvisorState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    num_messages: int = 0
    
class AlertsAgentState(AdvisorState):
    student_id: int
    upcoming_events: list[dict] = []
    student_interests: list[str] = []
    relivent_events: list[dict] = []
