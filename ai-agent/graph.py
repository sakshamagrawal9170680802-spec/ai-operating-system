from langgraph.graph import START,END,StateGraph
from state import Aegis_State
from nodes.chatbot_node import chatbot
from langchain.messages import HumanMessage,AIMessage,SystemMessage,ToolMessage
from langgraph.prebuilt import ToolNode,tools_condition
from nodes.chatbot_node import tools

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

Aegis_workflow=Aegis_graph.compile()
initial_state={"messages":[HumanMessage("Find the process using the most memory and give me its details.")]}
final_state=Aegis_workflow.invoke(initial_state)
print(final_state["messages"])