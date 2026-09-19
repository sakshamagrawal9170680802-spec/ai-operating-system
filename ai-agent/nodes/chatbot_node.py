from langchain_ollama import ChatOllama
from state import Aegis_State
from langchain.messages import SystemMessage
from System_Prompt import Aegis_System_Prompt
from tools.operating_system_tools import list_processes,get_system_memory,get_process_details,lock_computer,kill_process,find_process
from tools.brightness_tools import set_display_brightness,get_display_brightness,list_all_monitors
from tools.audio_tools import list_audio_output_devices,get_default_audio_device,get_volume,set_volume,get_mute_status,mute,unmute
from tools.dev_management_tools import open_application,arrange_windows,setup_dev_environment,get_open_windows,arrange_open_windows
from tools.file_management_tools import find_file_by_name
from tools.semantic_search.semantic_search_with_query import semantic_file_search

llm = ChatOllama(model="qwen3:4b",temperature=0)

tools=[list_processes,get_system_memory,get_process_details,set_display_brightness,get_display_brightness,list_all_monitors,list_audio_output_devices,get_default_audio_device,get_volume,set_volume,get_mute_status,mute,unmute,lock_computer,kill_process,find_process,open_application,arrange_windows,find_file_by_name,semantic_file_search,arrange_open_windows,get_open_windows,setup_dev_environment]

llm=llm.bind_tools(tools)

def chatbot(state:Aegis_State):
    messages=[
        SystemMessage(Aegis_System_Prompt),
        *state["messages"]
    ]
    response=llm.invoke(messages)
    return {"messages":[response]}
