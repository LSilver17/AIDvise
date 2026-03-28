from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from lg_agent.utilities.state import AlertsAgentState
from lg_agent.utilities.alert_nodes import get_new_events, get_interests, filter_relivent_events, insert_relevant_events

load_dotenv()

graph_builder = StateGraph(AlertsAgentState)

graph_builder.add_node("get_new_events", get_new_events)
graph_builder.add_node("get_interests", get_interests)
graph_builder.add_node("filter_relivent_events", filter_relivent_events)
graph_builder.add_node("insert_relevant_events", insert_relevant_events)

graph_builder.add_edge(START, "get_new_events")
graph_builder.add_edge(START, "get_interests")

graph_builder.add_edge("get_new_events", "filter_relivent_events")
graph_builder.add_edge("get_interests", "filter_relivent_events")

graph_builder.add_edge("filter_relivent_events", "insert_relevant_events")

graph_builder.add_edge("insert_relevant_events", END)

graph = graph_builder.compile()
