from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from langchain_anthropic import ChatAnthropic
from lg_agent.utilities.state import AdvisorState
from schemas import AdvisorOutputSchema

load_dotenv()

llm = ChatAnthropic(
    model="claude-sonnet-4-6",
    temperature=.2,
)

def advisor_node(state: AdvisorState) -> AdvisorState:
    """Base node for the academic advisor, decides whether it needs to use database queries or web search. If not, it answers the question directly using the knolledge it has."""
    
    structured_llm = llm.with_structured_output(AdvisorOutputSchema)

    system_prompt = ("""
        Listen to any questions the user has about course requirements, transfer guidelines, 
        and academic strategies. If you can answer the question directly, do so. If you need 
        to query the database to answer the question, set the 'requires_database' field to True 
        and specify what information you need from the database in the 'info_needed_db' field. 
        If you need to perform a web search to answer the question, set the 'requires_web_search' 
        field to True and specify what information you need to search for in the 'info_needed_web' 
        field. If you can answer the question directly, provide a clear and concise answer in the 
        'answer' field and set both 'requires_database' and 'requires_web_search' to False, while 
        leaving the 'info_needed_db' and 'info_needed_web' fields blank. Otherwise, leave the 
        'answer' field blank. Always set the 'requires_database' and 'requires_web_search' 
        fields accurately based on the information you need to answer the question.
    """)

    recent_messages = state["messages"][-10:]
    conversation_lines = []
    for message in recent_messages:
        message_type = getattr(message, "type", "")
        role = "User" if message_type == "human" else "Assistant"
        content = getattr(message, "content", "")
        if isinstance(content, list):
            content = " ".join(str(item) for item in content)
        conversation_lines.append(f"{role}: {content}")

    input = f"{system_prompt}\n\nConversation:\n" + "\n".join(conversation_lines)
    result = structured_llm.invoke(input)

    state["current_step"] = result
    artificial_response = AIMessage(content=result.json())
    state["messages"].append(artificial_response)
    state["num_messages"] += 1

    return state