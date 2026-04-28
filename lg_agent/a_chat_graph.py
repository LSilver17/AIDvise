import sys, os

# adds lg_agent directory to system path if not already there
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from lg_agent.utilities.state import AState
from langchain_core.messages import AIMessage
from lg_agent.utilities.nodes import a_planning_node
from db_helper_graph import db_graph
from web_helper_graph import web_graph

# cd my-agent && .venv\Scripts\activate && npx @langchain/langgraph-cli dev --port 8123 --no-browser
load_dotenv()

def invoke_db_helper(state: AState):
    """Function to invoke the database helper graph and return the results to the main graph."""
    db_helper_state = {"info_needed": state["plan"]["info_needed_db"], "messages": [], "loop_count": 0, "user_id": state["user_id"], "account_type": "Advisor"}
    result = db_graph.invoke(db_helper_state)
    db_info = state["db_info"]
    db_info.append(result["info"])
    return {"db_info": db_info}

def invoke_web_helper(state: AState):
    """Function to invoke the web helper graph and return the results to the main graph."""
    web_helper_state = {"info_needed": state["plan"]["info_needed_web"], "messages": [], "loop_count": 0}
    result = web_graph.invoke(web_helper_state)
    web_info = state["web_info"]
    web_info.append(result["info"])
    return {"web_info": web_info}

def route_from_planning(state: AState):
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

def answer_node(state: AState) -> AState:
    """Node that returns the final answer from the planning node."""
    return {"messages": state["messages"] + [AIMessage(content=state["plan"]["answer"])]}

graph_builder = StateGraph(AState)

graph_builder.add_node("planning", a_planning_node, defer=True)
graph_builder.add_node("invoke_db_helper", invoke_db_helper)
graph_builder.add_node("invoke_web_helper", invoke_web_helper)
graph_builder.add_node("answer_node", answer_node)

graph_builder.add_edge(START, "planning")
graph_builder.add_conditional_edges("planning", route_from_planning, ["invoke_db_helper", "invoke_web_helper", "answer_node"])
graph_builder.add_edge("invoke_db_helper", "planning")
graph_builder.add_edge("invoke_web_helper", "planning")
graph_builder.add_edge("answer_node", END)

a_chat_graph = graph_builder.compile()
