from langchain_core.messages import SystemMessage
from langchain_anthropic import ChatAnthropic
from langgraph.graph import END, START, MessagesState, StateGraph
async def mock_llm(state: MessagesState):
  model = ChatAnthropic(model="claude-sonnet-4-6")
  system_message = SystemMessage(content="You are a helpful assistant.")
  response = await model.ainvoke(
    [
      system_message,
      *state["messages"],
    ]
  )
  return {"messages": response}
graph = StateGraph(MessagesState)
graph.add_node(mock_llm)
graph.add_edge(START, "mock_llm")
graph.add_edge("mock_llm", END)
graph = graph.compile()