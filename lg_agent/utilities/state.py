from typing_extensions import TypedDict
from typing import Annotated
from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from utilities.schemas import RelevantEventsSchema

# States for the AdvisorAgent

class AdvisorState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
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