from langchain_core.tools import tool
import psutil
import ctypes
from guardrails import is_executable_protected
from langgraph.types import interrupt


@tool
def list_processes()->list[dict]:
    """
    Get all the running processes , sorted by memory usage

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

    return processes




@tool
def get_process_details(pid:int)->dict:
    """
    Get the current system memory usage.

    Returns:
        Total, available, used memory and memory usage percentage.
    """

    try:
        process=psutil.Process(pid)

        return {
            "pid": process.pid,
            "name": process.name(),
            "status": process.status(),
            "cpu_percent": process.cpu_percent(),
            "memory_percent": process.memory_percent(),
        }

    except(psutil.NoSuchProcess):
        return {"error":f"no such process exist with PID -- {pid}"}

    except(psutil.AccessDenied):
        return {"error":f"Access denied for process with PID -- {pid}"}


@tool
def find_process(name: str) -> list[dict]:
    """
    Find all currently running processes matching the given process name. sorted by memory usage

    Args:
        name: The name of the process to search for, for example
              'svchost.exe' or 'chrome.exe'.

    Returns:
        A list of dictionaries containing the PID and process name
        for every matching running process.
    """

    processes = []

    for process in psutil.process_iter(["pid", "name","cpu_percent","memory_percent"]):
        try:
            info=process.info
            process_name = info["name"]

            if process_name and process_name.lower() == name.lower():
                processes.append(info)

        except (psutil.NoSuchProcess,psutil.AccessDenied,psutil.ZombieProcess):
            continue

    processes.sort(key=lambda x:x["memory_percent"],reverse=True)# "key=lambda x:x["memory_percent"]" function based on which sorting is to be performed
    # reverse=True for decreasing order sorting

    return processes


@tool
def get_system_memory()->dict:
    """
    Get the current system memory usage.

    Returns:
        Total, available, used memory and memory usage percentage.
    """

    memory=psutil.virtual_memory()

    return {
        "total_gb":round(memory.total/(1024**3),2),
        "available_gb":round(memory.available/(1024**3),2),
        "used_gb":round(memory.used/(1024**3),2),
        "percent":memory.percent,
    }



@tool
def lock_computer() -> dict:
    """
    Lock the Windows workstation.
    """

    decision = interrupt("Do you want to lock the computer?")

    if not decision:
        return {
            "success": False,
            "cancelled": True,
            "message": "Computer lock cancelled by user."
        }
    try:
        result = ctypes.windll.user32.LockWorkStation()

        if result:
            return {
                "success": True,
                "message": "Computer locked successfully."
            }

        return {
            "success": False,
            "message": "Windows failed to lock the computer."
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to lock computer: {str(e)}"
        }


@tool
def kill_process(pid: int) -> dict:
    """
    Terminate a running process using its PID.

    Args:
        pid: The PID of the process to terminate.

    Returns:
        A dictionary describing whether the process was terminated,
        blocked by the guardrail, or could not be terminated.
    """
    try:
        process = psutil.Process(pid)
        process_name = process.name()

    except psutil.NoSuchProcess:
        return {
            "success": False,
            "blocked": False,
            "pid": pid,
            "message": f"No process exists with PID {pid}."
        }

    except psutil.AccessDenied:
        return {
            "success": False,
            "blocked": True,
            "pid": pid,
            "message": f"Access denied when inspecting PID {pid}."
        }
    
    protected, reason = is_executable_protected(pid)

    if protected:
        return {
            "success": False,
            "blocked": True,
            "message": reason
        }

    decision = interrupt(
        f"Do you want to terminate process '{process_name}' "
        f"(PID {pid})?"
    )
    if not decision:
        return {
            "success": False,
            "cancelled": True,
            "blocked": False,
            "pid": pid,
            "process": process_name,
            "message": "Process termination cancelled by user."
        }
    try:
        process.terminate()

        try:
            process.wait(timeout=3)

            return {
                "success": True,
                "blocked": False,
                "pid": pid,
                "process": process_name,
                "message": f"Process '{process_name}' with PID {pid} was terminated."
            }

        except psutil.TimeoutExpired:
            return {
                "success": False,
                "blocked": False,
                "pid": pid,
                "process": process_name,
                "message": f"Process '{process_name}' did not terminate within 3 seconds."
            }

    except psutil.NoSuchProcess:
        return {
            "success": False,
            "blocked": False,
            "pid": pid,
            "message": f"No process exists with PID {pid}."
        }

    except psutil.AccessDenied:
        return {
            "success": False,
            "blocked": False,
            "pid": pid,
            "message": f"Access denied when trying to terminate PID {pid}."
        }

    except Exception as e:
        return {
            "success": False,
            "blocked": False,
            "pid": pid,
            "message": f"Error terminating process: {str(e)}"
        }