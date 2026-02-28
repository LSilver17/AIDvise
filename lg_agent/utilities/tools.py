from dotenv import load_dotenv
from typing import TypedDict
from langchain_anthropic import ChatAnthropic
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
try:
    from .state import AdvisorState
except ImportError:
    from state import AdvisorState

load_dotenv()

db = SQLDatabase.from_uri("sqlite:///Test.db")

llm = ChatAnthropic(
    model="claude-sonnet-4-6",
    temperature=.2,
)

sqlToolkit = SQLDatabaseToolkit(db=db, llm=llm)
sql_tools = sqlToolkit.get_tools()

run_query_tool = next(tool for tool in sql_tools if tool.name == "sql_db_query")
run_query_node = ToolNode([run_query_tool], name="run_query")

querybot = llm.bind_tools([run_query_tool], tool_choice="any")

def generate_query(state: AdvisorState, k: int) -> str:
    response = querybot.invoke(
                [
                    SystemMessage(
                        """You are an agent designed to interact with a SQL database.
                        Given an input question, create a syntactically correct 
                        {dialect} query to run, then look at the results of the query 
                        and return the answer. Unless the user specifies a specific number 
                        of examples they wish to obtain, always limit your query to at most 
                        {k} results. You can order the results by a relevant column to 
                        return the most interesting examples in the database. Never query 
                        for all the columns from a specific table, only ask for the relevant 
                        columns given the question. DO NOT make any DML statements (INSERT, 
                        UPDATE, DELETE, DROP etc.) to the database.
                        The queery will be run in a later function, so just output the query 
                        as a string in your response.
                        """.format(dialect=db.dialect, k=k) + state["messages"][-1].content
                    )
                ]
    )
    return response.content

def query_check(query: str) -> str:
    response = querybot.invoke(
        [
            SystemMessage(
                """You are a SQL expert with a strong attention to detail. 
                Double check the {dialect} query for common mistakes, including: 
                - Using NOT IN with NULL values
                - Using UNION when UNION ALL should have been used
                - Using BETWEEN for exclusive ranges
                - Data type mismatch in predicates
                - Properly quoting identifiers
                - Using the correct number of arguments for functions
                - Casting to the correct data type
                - Using the proper columns for joins

                If there are any of the above mistakes, rewrite the query. 
                If there are no mistakes, just reproduce the original query.
                You will call the appropriate tool to execute the query after running this check.
                """.format(dialect=db.dialect)) + query
        ]
    )
    return response.content

@tool
def database_query(state: AdvisorState, k: int) -> AdvisorState:
    """
    Creates and runs a SQL query based on the user's question, then adds the results of the query to the agent's state so it can be used in future responses
    
    Args:
        k: the number of results to limit the query to
    """

    query = generate_query(state, k)
    checked_query = query_check(query)
    result = querybot.invoke_tool("sql_db_query", checked_query)
    return AdvisorState(
        messages=state["messages"] + [AIMessage(content=f"The database returned the following result for the query '{checked_query}': {result}")],
        num_calls=state["num_calls"]
    )