import sys, os
    
# adds utilities directory to system path if not already there
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# adds root directory to system path if not already there
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from utilities.state import AState, AdvisorState, DatabaseHelperState, WebSearchHelperState, InsertionHelperState
from utilities.schemas import APlanSchema, PlanSchema
from utilities.tools import db_tools, web_tools, insertion_tools, alt_db_tools
from utilities.model_inits import db_llm, planning_llm, web_llm, insertion_llm

load_dotenv()

def planning_node(state: AdvisorState) -> AdvisorState:
    """Base node for the agent when used by a student, decides whether it needs to use database queries or web search. If not, it answers the question directly using the knolledge it has."""
    
    state["plan"] = None

    structured_llm = planning_llm.with_structured_output(PlanSchema)

    system_prompt = f"You are an academic advisor assistant. Your task is to listen to any questions the user has about course requirements, transfer guidelines, academic strategies, etc. Respond according to the specified schema. If you can answer the user's question using informationed previously gathered, leave the appropriate fields blank, even if the answer pertains to the database or web. If loop count is 3 or higher and you still don't have the information needed, provide the best answer you can with the information you have and stop. In addition to answering questions, you should also listen to anything the user says about their interests and goals and use that information to update the database. Prioritise database info over web info where possible as it is more reliable. If web info is used, cite a source for it. If something fails to be retrieved from the database or web on the first attempt, do not try the same method of getting it more than once."

    messages = []
    messages.extend(state["messages"])

    if len(messages) == 0:
        messages.append(SystemMessage(content=system_prompt))

    if "db_info" not in state:
        state["db_info"] = []
    else:
        for QueryResult in state["db_info"]:
            messages.append(HumanMessage(content=f"Database Query: {QueryResult['query']}\nDatabase Result: {QueryResult['result']}"))
    if "web_info" not in state:
        state["web_info"] = []
    else:
        for QueryResult in state["web_info"]:
            messages.append(HumanMessage(content=f"Web Search Query: {QueryResult['query']}\nWeb Search Result: {QueryResult['result']}"))

    if state["insertion_result"] != "":
        messages.append(HumanMessage(content=f"Result of last insertion attempt: {state['insertion_result']}"))

    messages.append(HumanMessage(content="Current loop count: " + str(state["loop_count"])))

    response = structured_llm.invoke(messages).model_dump()
    state["plan"] = response
    state["loop_count"] += 1
    return state

def a_planning_node(state: AState) -> AState:
    """Base node for the agent when used by an advisor, decides whether it needs to use database queries or web search. If not, it answers the question directly using the knolledge it has."""
    
    structured_llm = planning_llm.with_structured_output(APlanSchema)

    system_prompt = f"You are the assitent to an academic advisor. Your task is to listen to the advisor's questions about student assigned to them and provide answers based on the information you have. You should also determine if you need to use database queries or web searches to get more information to answer the advisor's questions, and if so, which one would be most appropriate. If you can answer the advisor's question using information previously gathered, leave the appropriate fields blank, even if the answer pertains to the database or web. If loop count is 3 or higher and you still don't have the information needed, provide the best answer you can with the information you have and stop. Prioritise database info over web info where possible as it is more reliable. If web info is used, cite a source for it. If something fails to be retrieved from the database or web on the first attempt, do not try the same method of getting it more than once."
    messages = []
    messages.extend(state["messages"])

    if len(messages) == 0:
        messages.append(SystemMessage(content=system_prompt))

    if "db_info" not in state:
        state["db_info"] = []
    else:
        for QueryResult in state["db_info"]:
                messages.append(HumanMessage(content=f"Database Query: {QueryResult['query']}\nDatabase Result: {QueryResult['result']}"))
    if "web_info" not in state:
        state["web_info"] = []
    else:
        for QueryResult in state["web_info"]:
            messages.append(HumanMessage(content=f"Web Search Query: {QueryResult['query']}\nWeb Search Result: {QueryResult['result']}"))

    messages.append(HumanMessage(content="Current loop count: " + str(state["loop_count"])))

    response = structured_llm.invoke(messages).model_dump()
    state["plan"] = response
    state["loop_count"] += 1
    return state

def db_node(state: DatabaseHelperState):
    """Node that runs database queries based on the information provided by the planning node."""

    if state["account_type"] == "Student":
        llm_with_db_tools = db_llm.bind_tools(db_tools)
    else:
        llm_with_db_tools = db_llm.bind_tools(alt_db_tools)

    system_prompt = f"You are the assistant for a student academic advising agent. Your task is to determine how you can use the tools at your disposal to get the information it needs. Only output this information and nothing else. If loop count is 3 or higher and you still don't have the information needed, output what you have and stop. If a tool call fails on the first attempt, only retry it if it gives an exception message telling you how to fix it. If after a tool call fails if you don't think you can fix it by using different arguments or using a different tool, end early rather than running again."
    
    # if state messages is empty add a message with the info needed, otherwise pass the messages through
    if len(state["messages"]) == 0:
        state["messages"].append(SystemMessage(content=system_prompt))
        state["messages"].append(HumanMessage(content=f"The planning node has determined that the following information is needed from the database to answer the user's question: {state['info_needed']}"))

    messages = []
    messages.extend(state["messages"])

    messages.append(HumanMessage(content="Current loop count: " + str(state["loop_count"])))

    result = llm_with_db_tools.invoke(messages)

    state["loop_count"] += 1
    return {"messages": [result]}

def web_node(state: WebSearchHelperState):
    """Node that performs web searches based on the information provided by the planning node."""
    
    llm_with_web_tools = web_llm.bind_tools(web_tools)

    system_prompt = f"You are the assistant for a student academic advising agent. Your task is to determine how you can use web searches to get the information it needs. If multiple sources are available, choose the most recent and credible one. Only output the information you gather and its source, do not output anything else. If loop count is 3 or higher and you still don't have the information needed, output what you have and stop."

    # if state messages is empty add a message with the info needed, otherwise pass the messages through
    if len(state["messages"]) == 0:
        state["messages"].append(SystemMessage(content=system_prompt))
        state["messages"].append(HumanMessage(content=f"The planning node has determined that the following information is needed from the web to answer the user's question: {state['info_needed']}"))

    messages = []
    messages.extend(state["messages"])

    messages.append(HumanMessage(content="Current loop count: " + str(state["loop_count"])))

    result = llm_with_web_tools.invoke(messages)

    state["loop_count"] += 1
    return {"messages": [result]}

def insertion_node(state: InsertionHelperState) -> InsertionHelperState:
    """Node that takes any new information the advisor has learned about the student and inserts it into the database."""

    llm_with_insertion_tools = insertion_llm.bind_tools(insertion_tools)

    system_prompt = f"You are the assistant for an academic advising agent. Your task is to determine how you can use the following tools to update the database with any new information the advisor has learned about the student from their conversations and questions. If the information is already in the database, do not insert it again. Only output the tool calls and nothing else. If loop count is 3 or higher and you still have information that hasn't been inserted, leave it as is and stop."

    # if state messages is empty add a message with the info to be inserted, otherwise pass the messages through
    if len(state["messages"]) == 0:
        state["messages"].append(SystemMessage(content=system_prompt))
        state["messages"].append(HumanMessage(content=f"The planning node has determined that the following information about the student should be added into the database if it is not already present: {state['info_to_insert']}"))
    
    messages = []
    messages.extend(state["messages"])

    messages.append(HumanMessage(content="Current loop count: " + str(state["loop_count"])))

    result = llm_with_insertion_tools.invoke(messages)

    state["loop_count"] += 1
    return {"messages": [result]}
