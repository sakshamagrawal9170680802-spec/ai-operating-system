from typing import TypedDict,Annotated
from langgraph.graph.message import add_messages

class Aegis_State(TypedDict):
    messages:Annotated[list,add_messages]# here add_messsage is a reducer function that tells what to do woth new value going to enter list whether to append it or write it
