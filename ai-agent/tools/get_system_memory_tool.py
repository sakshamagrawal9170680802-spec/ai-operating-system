from langchain_core.tools import tool
import psutil

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