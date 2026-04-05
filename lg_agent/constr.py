import sys, os
from typing import Literal

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from utilities.state import AdvisorInput, AdvisorState
from utilities.nodes import planning_node, answer_node
from db_helper_graph import db_graph
from web_helper_graph import web_graph

# cd my-agent && .venv\Scripts\activate && npx @langchain/langgraph-cli dev --port 8123 --no-browser
load_dotenv()

def invoke_db_helper(state: AdvisorState):
    """Function to invoke the database helper graph and return the results to the main graph."""
    db_helper_state = {"info_needed": state["plan"]["info_needed_db"], "messages": []}
    result = db_graph.invoke(db_helper_state)
    db_info = state["db_info"]
    db_info.append(result["info"])
    return {"db_info": db_info}

def invoke_web_helper(state: AdvisorState):
    """Function to invoke the web helper graph and return the results to the main graph."""
    web_helper_state = {"info_needed": state["plan"]["info_needed_web"]}
    result = web_graph.invoke(web_helper_state)
    web_info = state["web_info"]
    web_info.append(result["info"])
    return {"web_info": web_info}

def route_from_planning(state: AdvisorState):
    """
    Routing function to determine which helper graph(s) to invoke based on the output of the planning node. If the planning 
    node indicates that information is needed from the database, the database helper graph will be invoked. If it indicates 
    that information is needed from the web, the web helper graph will be invoked. If it indicates that both are needed, the 
    they will be run in parallel. If neither are needed, the graph will route directly to the answer node.
    """
    routes = []
    if state["plan"]["requires_database"]:
        routes.append("invoke_db_helper")
    if state["plan"]["requires_web_search"]:
        routes.append("invoke_web_helper") 
    if not routes:
        routes.append("answer_node")
    return [Send(route, state) for route in routes]

graph_builder = StateGraph(AdvisorState)

graph_builder.add_node("planning", planning_node)
graph_builder.add_node("invoke_db_helper", invoke_db_helper)
graph_builder.add_node("invoke_web_helper", invoke_web_helper)
graph_builder.add_node("answer_node", answer_node)

graph_builder.add_edge(START, "planning")
graph_builder.add_conditional_edges("planning", route_from_planning)
graph_builder.add_edge("invoke_db_helper", "answer_node")
graph_builder.add_edge("invoke_web_helper", "answer_node")
graph_builder.add_edge("answer_node", END)

graph = graph_builder.compile()
