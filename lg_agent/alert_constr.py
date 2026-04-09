import sys, os
    
# adds lg_agent directory to system path if not already there
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from utilities.state import AlertsAgentInput, AlertsAgentState, AlertsAgentOutput
from utilities.alert_nodes import get_new_events, get_interests, filter_relivent_events, insert_relevant_events

load_dotenv()

def state_initializer(input: AlertsAgentInput) -> AlertsAgentState:
    return {"student_id": input["student_id"], "upcoming_events": [], "student_interests": [], "relevant_events": []}

def checkpoint(state: AlertsAgentState) -> AlertsAgentState:
    return state

def end_early_check(state: AlertsAgentState):
    if len(state["upcoming_events"]) == 0:
        if len(state["student_interests"]) == 0:
            print("No upcoming events or student interests, ending graph.")
            return END
        print("No upcoming events, ending graph.")
        return END
    elif len(state["student_interests"]) == 0:
        print("No student interests, ending graph.")
        return END
    else:
        return "filter_relivent_events"

def format_response(state: AlertsAgentState) -> AlertsAgentOutput:
    return {"relevant_events": state["relevant_events"]}

graph_builder = StateGraph(AlertsAgentState, input_schema=AlertsAgentInput, output_schema=AlertsAgentOutput)

graph_builder.add_node("state_initializer", state_initializer)
graph_builder.add_node("get_new_events", get_new_events)
graph_builder.add_node("get_interests", get_interests)
graph_builder.add_node("checkpoint", checkpoint, defer=True)
graph_builder.add_node("filter_relivent_events", filter_relivent_events)
graph_builder.add_node("insert_relevant_events", insert_relevant_events)
graph_builder.add_node("format_response", format_response)

graph_builder.add_edge(START, "state_initializer")
graph_builder.add_edge("state_initializer", "get_new_events")
graph_builder.add_edge("state_initializer", "get_interests")
graph_builder.add_edge("get_new_events", "checkpoint")
graph_builder.add_edge("get_interests", "checkpoint")
graph_builder.add_conditional_edges("checkpoint", end_early_check, ["filter_relivent_events", END])
graph_builder.add_edge("filter_relivent_events", "insert_relevant_events")
graph_builder.add_edge("insert_relevant_events", "format_response")
graph_builder.add_edge("format_response", END)

alert_graph = graph_builder.compile()
