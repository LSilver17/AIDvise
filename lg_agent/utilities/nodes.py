from dotenv import load_dotenv
from langchain_core.messages import AIMessage, SystemMessage
from langchain_anthropic import ChatAnthropic
from langgraph.graph import END
from lg_agent.utilities.state import AdvisorState
from schemas import AdvisorOutputSchema
from typing_extensions import Literal
from lg_agent.utilities.tools import db_tools

load_dotenv()

llm = ChatAnthropic(
    model="claude-sonnet-4-6",
    temperature=.2,
)

def planning_node(state: AdvisorState) -> AdvisorState:
    """Base node for the academic advisor, decides whether it needs to use database queries or web search. If not, it answers the question directly using the knolledge it has."""
    
    structured_llm = llm.with_structured_output(AdvisorOutputSchema)

    system_prompt = "You are an academic advisor assistant. Your task is to listen to any questions the user has about course requirements, transfer guidelines, academic strategies, etc. Then respond according to the specified schema."

    db_info = "Database information gathered so far: "
    web_info = "Web information gathered so far: "

    for db_query, db_result in state["db_info"].items():
        db_info += f"\nQuery: {db_query}\nResult: {db_result}\n"
    
    for web_query, web_result in state["web_info"].items():
        web_info += f"\nQuery: {web_query}\nResult: {web_result}\n"

    messages = []
     
    messages.append(SystemMessage(content=system_prompt))
    messages.append(SystemMessage(content=f"{db_info}\n\n{web_info}"))

    messages.extend(state["messages"])

    response = structured_llm(messages).to_dict()
    state["plan"] = response["structured_output"]
    return state

def db_node(state: AdvisorState) -> AdvisorState:
    """Node that runs database queries based on the information provided by the planning node."""

    llm_with_db_tools = llm.bind_tools(db_tools)

    system_prompt = "You are the assistant for a student academic advising agent. Your task is to determine how you can use the tools at your disposal to get the information needed to answer the student's question, based on the information provided by the planning node. You should compile the relevant information from the database queries you perform into a clear and concise format that can be used by the answer node to formulate a final answer to the student's question.\nHere are the tools you have at your disposal:"

    for tool in db_tools:
        system_prompt += f"\n\nTool Name: {tool.name}\nDescription: {tool.description}"
    
    input = f"{system_prompt}\n\nThe planning node has determined that the following information is needed from the database to answer the user's question: {state["plan"]["info_needed_db"]}"

    result = llm_with_db_tools.invoke(input)

    state["db_info"] = {"query": state["plan"]["info_needed_db"], "results": result}

    return state

def web_node(state: AdvisorState) -> AdvisorState:
    """Node that performs web searches based on the information provided by the planning node."""
    # TODO: implement web search node

    return state

def answer_node(state: AdvisorState) -> AdvisorState:
    """Node that formulates a final answer based on the information gathered from the planning node, database node, and web node."""

    # Check if the planning node was able to answer the question directly
    if not state["plan"]["requires_database"] and not state["plan"]["requires_web_search"] and state["plan"]["answer"] != "":
        state["messages"].append(AIMessage(content=f"{state['plan']['answer']}"))
        return END
    
    # Otherwise formulate an answer based on the information from the database and web nodes

    system_prompt = "You are an academic advisor assistant. Your task is to listen to any questions the user has about course requirements, transfer guidelines, academic strategies, etc. Then respond according to information gathered from database and web searches."

    db_info = "Database information gathered: "
    web_info = "Web information gathered: "

    for db_query, db_result in state["db_info"].items():
        db_info += f"\nQuery: {db_query}\nResult: {db_result}\n"
    
    for web_query, web_result in state["web_info"].items():
        web_info += f"\nQuery: {web_query}\nResult: {web_result}\n"

    messages = []
     
    messages.append(SystemMessage(content=system_prompt))
    messages.append(SystemMessage(content=f"{db_info}\n\n{web_info}"))

    messages.append(state["messages"][-1]) # add the user's original question

    answer = llm.invoke(messages)
    state["messages"].append(AIMessage(content=answer))
    state["num_messages"] += 1
    return state