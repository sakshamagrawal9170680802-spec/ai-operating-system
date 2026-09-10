import psutil
from langchain_core.tools import tool


@tool
def list_processes()->list[dict]:
    """
    Get the Top 10 running processes using the most CPU or memory

    Returns:
        A List containing each process name, PID, CPU usage and memory usage in form of python dictionary
         
    """
    processes=[]

    for process in psutil.process_iter(["pid","name","cpu_percent","memory_percent"]):

        try:
            info=process.info # as each process is of <class psutil.Process> data type and process.info is of python dictionary data type so making it easier to access each value

            processes.append(info)

        except(psutil.NoSuchProcess,psutil.AccessDenied):
            continue


        processes.sort(key=lambda x:x["memory_percent"],reverse=True)# "key=lambda x:x["memory_percent"]" function based on which sorting is to be performed
        # reverse=True for decreasing order sorting

        return processes[0:10]# to get top 10 processes