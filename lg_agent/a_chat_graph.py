import sys, os

# adds lg_agent directory to system path if not already there
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from lg_agent.utilities.state import APlannerState
from langchain_core.messages import AIMessage
from lg_agent.utilities.nodes import a_planner_node
from db_helper_graph import db_graph
from web_helper_graph import web_graph

# cd my-agent && .venv\Scripts\activate && npx @langchain/langgraph-cli dev --port 8123 --no-browser
load_dotenv()

def invoke_db_helper(state: APlannerState):
    """
    Invokes the advisor database helper graph and merges its result back into state.

    The advisor planner may request database information about a student or course.
    This node forwards that request to the database helper graph, then appends the
    returned query/result pair to the accumulated db_info list.

    Args:
        state (APlannerState): Current planner state containing the selected database
            request in plan["info_needed_db"].

    Returns:
        dict: Partial state update with the updated "db_info" list.
    """
    db_helper_state = {"info_needed": state["plan"]["info_needed_db"], "messages": [], "loop_count": 0, "user_id": state["user_id"], "account_type": "Advisor"}
    result = db_graph.invoke(db_helper_state)
    db_info = state["db_info"]
    db_info.append(result["info"])
    return {"db_info": db_info}

def invoke_web_helper(state: APlannerState):
    """
    Invokes the web helper graph and merges its result back into state.

    The advisor planner may request web information to support an answer. This node
    forwards that request to the web helper graph, then appends the returned
    query/result pair to the accumulated web_info list.

    Args:
        state (APlannerState): Current planner state containing the selected web
            request in plan["info_needed_web"].

    Returns:
        dict: Partial state update with the updated "web_info" list.
    """
    web_helper_state = {"info_needed": state["plan"]["info_needed_web"], "messages": [], "loop_count": 0}
    result = web_graph.invoke(web_helper_state)
    web_info = state["web_info"]
    web_info.append(result["info"])
    return {"web_info": web_info}

def route_from_planning(state: APlannerState):
    """
    Chooses which helper graphs to run after planning.

    The planner can request database lookups or web lookups, or provide a final
    answer directly. This router converts the plan into one or more graph sends.
    When both database and web information are requested, they are dispatched in
    parallel. If no tools are needed, control routes directly to the answer node.

    Args:
        state (APlannerState): Current planner state containing the loop counter and
            the structured plan produced by the planning node.

    Returns:
        list[Send]: One or more graph sends describing the next execution branch.
    """
    if state["loop_count"] < 3:
        routes = []
        if "requires_database" in state["plan"] and state["plan"]["requires_database"]:
            routes.append("invoke_db_helper")
        if "requires_web_search" in state["plan"] and state["plan"]["requires_web_search"]:
            routes.append("invoke_web_helper")
        if not routes:
            routes.append("answer_node")
        return [Send(route, state) for route in routes]
    elif "answer" in state["plan"] and state["plan"]["answer"] is not None and state["plan"]["answer"] != "":
        return [Send("answer_node", state)]
    else:
        if state["loop_count"] == 3:
            messages = state["messages"] + [AIMessage(content="You went over the loop limit. Give your final answer now.")]
            return [Send("planning", {"messages": messages, "loop_count": state["loop_count"] + 1})]
        else:
            messages = AIMessage(content="Failsafe: AI broke the rules. Please try to rephrase your question.")
            return [Send("answer_node", {"messages": [messages]})]

def answer_node(state: APlannerState) -> APlannerState:
    """
    Appends the final planner answer to the conversation state.

    Args:
        state (APlannerState): Current planner state containing the final answer in
            plan["answer"].

    Returns:
        APlannerState: Updated state with the final AI answer appended to messages.
    """
    return {"messages": state["messages"] + [AIMessage(content=state["plan"]["answer"])]}

graph_builder = StateGraph(APlannerState)

graph_builder.add_node("planning", a_planner_node, defer=True)
graph_builder.add_node("invoke_db_helper", invoke_db_helper)
graph_builder.add_node("invoke_web_helper", invoke_web_helper)
graph_builder.add_node("answer_node", answer_node)

graph_builder.add_edge(START, "planning")
graph_builder.add_conditional_edges("planning", route_from_planning, ["invoke_db_helper", "invoke_web_helper", "answer_node"])
graph_builder.add_edge("invoke_db_helper", "planning")
graph_builder.add_edge("invoke_web_helper", "planning")
graph_builder.add_edge("answer_node", END)

a_chat_graph = graph_builder.compile()
