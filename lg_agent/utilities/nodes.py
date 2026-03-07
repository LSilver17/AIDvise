from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from langchain_anthropic import ChatAnthropic
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
try:
    from .state import AdvisorState
except ImportError:
    from state import AdvisorState

load_dotenv()

try:
    db = SQLDatabase.from_uri("sqlite:///Test.db")
except Exception as exc:
    raise RuntimeError(
        "Failed to initialize database connection from URI 'sqlite:///Test.db'. "
        "Verify that the SQLite file exists and is readable."
    ) from exc

llm = ChatAnthropic(
    model="claude-sonnet-4-6",
    temperature=.2,
    tools= [{
        "type": "web_search_20260209",
        "name": "web_search",
        "max_uses": 3
    }]
)


ChatBot = create_sql_agent(
    llm,
    db=db,
    verbose=True,
    agent_executor_kwargs={"handle_parsing_errors": True}
)

def advisor_node(state: AdvisorState):
    """Takes the role of an academic advisor, augmented with search tools to deliver information about colleges"""

    system_prompt = (
        "Listen to any questions they have about course requirements, transfer guidelines, "
        "and academic strategies, utilizing the search tool to take information off official "
        "college websites when necessary. Responses should be objective and concise. Alert "
        "the user when they have run out of search uses. You have access to a database "
        "containing information about courses offered in each term."
    )

    recent_messages = state["messages"][-10:]
    conversation_lines = []
    for message in recent_messages:
        message_type = getattr(message, "type", "")
        role = "User" if message_type == "human" else "Assistant"
        content = getattr(message, "content", "")
        if isinstance(content, list):
            content = " ".join(str(item) for item in content)
        conversation_lines.append(f"{role}: {content}")

    input_text = f"{system_prompt}\n\nConversation:\n" + "\n".join(conversation_lines)
    result = ChatBot.invoke({"input": input_text})

    output_text = result.get("output") if isinstance(result, dict) else str(result)
    return {
        "messages": [AIMessage(content=output_text or "")],
        "num_messages": state.get("num_messages", 0) + 1
    }
