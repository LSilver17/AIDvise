"""
Copyright 2026 Luca Silver

Constructs the alerts agent graph that filters upcoming events based on student interests.

Functions:
- `state_initializer`: Initializes alerts agent state with empty containers for events and interests.
- `checkpoint`: Synchronization node using defer=True to wait for parallel tasks completion.
- `end_early_check`: Conditional router that skips event filtering if no events or interests are present.
- `format_response`: Formats the final state into the alerts agent output schema.

Graph Structure:
- START -> state_initializer
- state_initializer -> [get_new_events | get_interests] (parallel)
- get_new_events -> checkpoint (deferred)
- get_interests -> checkpoint (deferred)
- checkpoint -> [filter_relivent_events | END] (conditional - early termination if no events/interests)
- filter_relivent_events -> insert_relevant_events
- insert_relevant_events -> format_response
- format_response -> END

Exports:
- `alert_graph`: Compiled LangGraph alerts agent.
"""

import sys, os

# adds lg_agent directory to system path if not already there
PARENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PARENT_DIR not in sys.path:
    sys.path.append(PARENT_DIR)

from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from utilities.state import AlertsAgentInput, AlertsAgentState, AlertsAgentOutput
from utilities.alert_nodes import get_new_events, get_interests, filter_relivent_events, insert_relevant_events

load_dotenv()

def state_initializer(input: AlertsAgentInput) -> AlertsAgentState:
    """
    Initializes the alerts agent state from user input.
    
    Creates the initial state dictionary for the alerts agent with empty containers
    for upcoming events, interests, and relevant events. This state will be populated
    by subsequent nodes in the graph.
    
    Args:
        input (AlertsAgentInput): Input schema containing:
            - 'student_id': Integer ID of the student to process alerts for
    
    Returns:
        AlertsAgentState: Initial state dictionary with:
            - 'student_id': The provided student ID
            - 'upcoming_events': Empty list (will be populated by get_new_events)
            - 'student_interests': Empty list (will be populated by get_interests)
            - 'relevant_events': Empty list (will be populated by filter_relivent_events)
    """
    return {"student_id": input["student_id"], "upcoming_events": [], "student_interests": [], "relevant_events": []}

def checkpoint(state: AlertsAgentState) -> AlertsAgentState:
    """
    Checkpoint node that ensures parallel tasks complete before proceeding.
    
    This node uses the defer=True mechanism to act as a synchronization point,
    allowing the graph to merge the parallel results from get_new_events and 
    get_interests before proceeding to the conditional routing logic.
    
    Args:
        state (AlertsAgentState): The current state with events and interests populated.
    
    Returns:
        AlertsAgentState: The unchanged state, passed through to the next conditional node.
    """
    return state

def end_early_check(state: AlertsAgentState):
    """
    Conditional router that determines whether to continue processing or end early.
    
    Examines the state to decide if there's sufficient data to proceed with event
    filtering. Ends the graph early if there are no upcoming events or no student
    interests, as filtering cannot produce meaningful results without both.
    
    Args:
        state (AlertsAgentState): The current state with populated events and interests.
    
    Returns:
        str or END: 
            - "filter_relivent_events": If both events and interests exist, proceed to filtering
            - END: If either events or interests are empty, terminate the graph
    
    Note:
        This function logs reasons for early termination to aid in debugging.
    """
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
    """
    Formats the final state into the agent's output schema.
    
    Extracts the relevant events from the final state and returns them in the
    format specified by AlertsAgentOutput. This serves as the final node before
    the graph completes, ensuring the output conforms to the expected interface.
    
    Args:
        state (AlertsAgentState): The final state containing the processed relevant_events.
    
    Returns:
        AlertsAgentOutput: Output schema dictionary with 'relevant_events' key containing
            the list of events relevant to the student.
    """
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
