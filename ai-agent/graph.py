from langgraph.graph import START,END,StateGraph
from state import Aegis_State
from nodes.chatbot_node import chatbot
from langchain.messages import HumanMessage,AIMessage,SystemMessage,ToolMessage
from langgraph.prebuilt import ToolNode,tools_condition
from nodes.chatbot_node import tools
from dotenv import load_dotenv
import os
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg import connect
from psycopg.rows import dict_row

load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL is not set in the .env file."
    )


#graph creation
Aegis_graph=StateGraph(Aegis_State)


#adding nodes to graph
Aegis_graph.add_node("chatbot",chatbot)
Aegis_graph.add_node("Aegis_tools",ToolNode(tools,messages_key="messages"))

#adding edges to connect nodes in graph
Aegis_graph.add_edge(START,"chatbot")
Aegis_graph.add_edge("chatbot",END)
Aegis_graph.add_conditional_edges("chatbot",tools_condition,{"tools":"Aegis_tools",END:END})
Aegis_graph.add_edge("Aegis_tools","chatbot")


#creating checkpointer to save messages and add persistence
connection=connect(DATABASE_URL,autocommit=True,row_factory=dict_row)
checkpointer=PostgresSaver(connection)
checkpointer.setup()


#compile graph
agent=Aegis_graph.compile(checkpointer=checkpointer)
