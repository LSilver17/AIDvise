import sys, os

# adds lg_agent directory to system path if not already there
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from lg_agent.s_chat_graph import chat_graph
from langchain.messages import HumanMessage

chat_graph.invoke({"messages": [HumanMessage(content="I love pottery")]})