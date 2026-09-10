from langchain_core.tools import tool
import psutil

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
