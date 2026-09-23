import screen_brightness_control as sbc
from langchain_core.tools import tool
from langgraph.types import interrupt

@tool
def set_display_brightness(level:int)->dict:
    """
    Set the Screen Brightness to a specific percentage.

    Args:
        level: Brightness level from 0 to 100

    Returns:
        Result of Brightness change 
    """

    if level<0 or level>100:
        return {
            "success": False,
            "message": "Brightness level must be between 0 and 100"
        }
    
    decision = interrupt(f"Do you want to set the display brightness to {level}%?")

    if not decision:
        return {
            "success": False,
            "cancelled": True,
            "message": "Brightness change cancelled by user."
        }
    try:

        sbc.set_brightness(level)

        return {
            "success": True,
            "brightness": level,
            "message": f"Brightness set to {level}%."
        }

        
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to set Brightness: {str(e)}"
        }


@tool
def get_display_brightness()->dict:
    """
    Get the Screen Brightness percentage of your monitor or display.

    Returns:
        Brightness percentage of monitor or display
    """
    
    try:
        level=sbc.get_brightness()
        return {
            "success": True,
            "brightness": level,
            "message": f"Brightness level is {level}%."
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to get Brightness: {str(e)}"
        }


@tool
def list_all_monitors()->list[str]:
    """
     Get information about all connected monitors.

    Returns:
        A list containing monitor identifier.
    """

    try:
        return sbc.list_monitors()

    except Exception as e:
        return [f"Failed to detect monitors: {str(e)}"]