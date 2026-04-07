import sys, os
    
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_anthropic import ChatAnthropic
from utilities.state import AdvisorState, DatabaseHelperState, WebSearchHelperState
from utilities.schemas import PlanSchema
from utilities.tools import db_tools, web_tools

load_dotenv()

llm = ChatAnthropic(
    model="claude-sonnet-4-6",
    temperature=.2,
)

db_llm = ChatAnthropic(
    model="claude-sonnet-4-6",
    temperature=.2,
)

web_llm = ChatAnthropic(
    model="claude-sonnet-4-6",
    temperature=.2,
)

def planning_node(state: AdvisorState) -> AdvisorState:
    """Base node for the academic advisor, decides whether it needs to use database queries or web search. If not, it answers the question directly using the knolledge it has."""
    
    structured_llm = llm.with_structured_output(PlanSchema)

    system_prompt = f"You are an academic advisor assistant. Your task is to listen to any questions the user has about course requirements, transfer guidelines, academic strategies, etc. Respond according to the specified schema. If you can answer the user's question using informationed previously gathered, leave the appropriate fields blank, even if the answer pertains to the database or web. If loop count is 3 or higher and you still don't have the information needed, provide the best answer you can with the information you have and stop. loop count = {state['loop_count']}"

    messages = []
     
    messages.append(SystemMessage(content=system_prompt))

    for QueryResult in state["db_info"]:
        messages.append(SystemMessage(content=f"Database Query: {QueryResult['query']}\nDatabase Result: {QueryResult['result'].content}"))
    for QueryResult in state["web_info"]:
        messages.append(SystemMessage(content=f"Web Search Query: {QueryResult['query']}\nWeb Search Result: {QueryResult['result'].content}"))

    messages.extend(state["messages"])

    response = structured_llm.invoke(messages).model_dump()
    state["plan"] = response
    state["loop_count"] += 1
    return state

def db_node(state: DatabaseHelperState):
    """Node that runs database queries based on the information provided by the planning node."""

    llm_with_db_tools = db_llm.bind_tools(db_tools)

    system_prompt = f"You are the assistant for a student academic advising agent. Your task is to determine how you can use the tools at your disposal to get the information it needs. Only output this information and nothing else. If loop count is 3 or higher and you still don't have the information needed, output what you have and stop. loop count = {state['loop_count']}"
    
    # if state messages is empty add a message with the info needed, otherwise pass the messages through
    if len(state["messages"]) == 0:
        state["messages"].append(HumanMessage(content=f"The planning node has determined that the following information is needed from the database to answer the user's question: {state['info_needed']}"))

    messages = [SystemMessage(content=system_prompt)]
    messages.extend(state["messages"])

    result = llm_with_db_tools.invoke(messages)

    state["loop_count"] += 1
    return {"messages": [result]}

def web_node(state: WebSearchHelperState):
    """Node that performs web searches based on the information provided by the planning node."""
    
    llm_with_web_tools = web_llm.bind_tools(web_tools)

    system_prompt = f"You are the assistant for a student academic advising agent. Your task is to determine how you can use web searches to get the information it needs. Only output this information and nothing else. If loop count is 3 or higher and you still don't have the information needed, output what you have and stop. loop count = {state['loop_count']}"

    # if state messages is empty add a message with the info needed, otherwise pass the messages through
    if len(state["messages"]) == 0:
        state["messages"].append(HumanMessage(content=f"The planning node has determined that the following information is needed from the web to answer the user's question: {state['info_needed']}"))

    messages = [SystemMessage(content=system_prompt)]
    messages.extend(state["messages"])

    result = llm_with_web_tools.invoke(messages)

    state["loop_count"] += 1
    return {"messages": [result]}
