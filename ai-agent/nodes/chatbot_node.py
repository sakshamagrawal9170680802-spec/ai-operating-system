from langchain_ollama import ChatOllama
from dotenv import load_dotenv
import os
from state import Aegis_State
from langchain.messages import SystemMessage
from System_Prompt import Aegis_System_Prompt
from tools.list_processes_tool import list_processes
from tools.get_system_memory_tool import get_system_memory
from tools.get_PID_process_details_tool import get_process_details


load_dotenv()

api_key=os.getenv("OLLAMA_API_KEY")


llm=ChatOllama(model="gpt-oss:120b",
               base_url="https://ollama.com",
               temperature=0,
               client_kwargs={
                    "headers": {
                        "Authorization": f"Bearer {api_key}"
                    }
                }
    )

tools=[list_processes,get_system_memory,get_process_details]

llm=llm.bind_tools(tools)

def chatbot(state:Aegis_State):
    messages=[
        SystemMessage(Aegis_System_Prompt),
        *state["messages"]
    ]
    response=llm.invoke(messages)
    return {"messages":[response]}