import subprocess # works with operating system API to open different softwares
from langchain.tools import tool
from langgraph.types import interrupt
import pygetwindow as gw # is able to get currently open apps and manipulate its windowsize and location Windows window-management API
import ctypes
import time


ALLOWED_APPS = {
    "vscode": ["code"],
    "notepad": ["notepad.exe"],
    "word": [r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE"],
    "chrome": ["chrome.exe"],
    "calculator": ["calc.exe"],
    "file explorer": ["explorer.exe"],
    "docker": [r"C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe"],
}

APP_TITLES = { 
    "vscode": ["visual studio code"],
    "docker": ["docker desktop"],
    "chrome": ["google chrome"],
    "notepad": ["notepad"],
    "word": ["microsoft word"],
    "calculator": ["calculator"],
    "file explorer": ["file explorer"],
}

@tool
def get_open_windows() -> dict:
    """
    Return all currently open application windows on the desktop.

    This tool does not restrict applications to Aegis's supported
    application list. It discovers all visible windows currently
    open on the system.
    """

    try:
        windows = gw.getAllWindows()

        open_applications = []

        for window in windows:

            title = window.title.strip()

            if not title:
                continue

            if window.isMinimized:
                continue

            open_applications.append({
                "title": title,
                "left": window.left,
                "top": window.top,
                "width": window.width,
                "height": window.height,
            })

        return {
            "success": True,
            "applications": open_applications,
            "count": len(open_applications),
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Could not get open applications: {e}"
        }


@tool
def open_application(application: str) -> dict:
    """
    Open an allowed desktop application.

    Supported applications include:
    - vscode
    - notepad
    - word
    - chrome
    - calculator
    - file explorer
    - docker

    Args:
        application: The name of the application to open.

    Returns:
        A dictionary describing whether the application was opened,
        cancelled by the user, or could not be opened.
    """

    application = application.lower().strip()

    aliases = {
        "microsoft word": "word",
        "ms word": "word",
        "word": "word",

        "visual studio code": "vscode",
        "vs code": "vscode",

        "google chrome": "chrome",
        "chrome": "chrome",

        "notepad": "notepad",

        "calculator": "calculator",

        "file explorer": "file explorer",
        "explorer": "file explorer",

        "docker desktop": "docker",
        "docker": "docker",
    }

    application = aliases.get(application, application)

    print("DEBUG application:", repr(application))
    print("DEBUG command:", ALLOWED_APPS.get(application))

    if application not in ALLOWED_APPS:
        return {
            "success": False,
            "message": f"Opening '{application}' is not allowed."
        }

    decision = interrupt(
        f"Do you want to open {application}?"
    )

    if not decision:
        return {
            "success": False,
            "cancelled": True,
            "message": f"Open {application} command cancelled by user."
        }

    try:
        process = subprocess.Popen(ALLOWED_APPS[application])

        return {
            "success": True,
            "application": application,
            "pid": process.pid,
            "message": f"{application} opened successfully."
        }

    except FileNotFoundError:
        return {
            "success": False,
            "message": f"{application} executable could not be found."
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Could not open {application}: {e}"
        }

def _arrange_window_objects(
    windows: list,
    layout: str
) -> dict:

    try:
        class RECT(ctypes.Structure):
            _fields_ = [
                ("left", ctypes.c_long),
                ("top", ctypes.c_long),
                ("right", ctypes.c_long),
                ("bottom", ctypes.c_long),
            ]

        rect = RECT()

        ctypes.windll.user32.SystemParametersInfoW(
            0x0030,
            0,
            ctypes.byref(rect),
            0
        )

        screen_left = rect.left
        screen_top = rect.top

        screen_width = rect.right - rect.left
        screen_height = rect.bottom - rect.top

        if layout == "two_columns":

            half_width = screen_width // 2

            zones = [
                (
                    screen_left,
                    screen_top,
                    half_width,
                    screen_height
                ),
                (
                    screen_left + half_width,
                    screen_top,
                    screen_width - half_width,
                    screen_height
                ),
            ]

        elif layout == "three_columns":

            third_width = screen_width // 3

            zones = [
                (
                    screen_left,
                    screen_top,
                    third_width,
                    screen_height
                ),
                (
                    screen_left + third_width,
                    screen_top,
                    third_width,
                    screen_height
                ),
                (
                    screen_left + third_width * 2,
                    screen_top,
                    screen_width - third_width * 2,
                    screen_height
                ),
            ]

        elif layout == "four_quarters":

            half_width = screen_width // 2
            half_height = screen_height // 2

            zones = [
                # top-left
                (
                    screen_left,
                    screen_top,
                    half_width,
                    half_height
                ),

                # top-right
                (
                    screen_left + half_width,
                    screen_top,
                    screen_width - half_width,
                    half_height
                ),

                # bottom-left
                (
                    screen_left,
                    screen_top + half_height,
                    half_width,
                    screen_height - half_height
                ),

                # bottom-right
                (
                    screen_left + half_width,
                    screen_top + half_height,
                    screen_width - half_width,
                    screen_height - half_height
                ),
            ]

        else:
            return {
                "success": False,
                "message": f"Unknown layout: {layout}"
            }

        arranged = []

        for window, zone in zip(windows, zones):

            x, y, width, height = zone

            if window.isMinimized or window.isMaximized:
                window.restore()

            window.resizeTo(width, height)
            window.moveTo(x, y)

            arranged.append(window.title)

        return {
            "success": True,
            "message": "Open windows arranged successfully.",
            "layout": layout,
            "arranged_windows": arranged
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Could not arrange windows: {e}"
        }

@tool
def arrange_open_windows() -> dict:
    """
    Arrange currently open application windows automatically.

    The tool detects currently open windows and chooses a layout
    based on the number of windows.

    2 windows -> two_columns
    3 windows -> three_columns
    4 windows -> four_quarters

    The arrangement is performed only after user confirmation.
    """

    try:
        windows = gw.getAllWindows()

        open_windows = []

        for window in windows:

            title = window.title.strip()

            # Ignore windows without a title
            if not title:
                continue

            # Ignore minimized windows
            if window.isMinimized:
                continue

            open_windows.append(window)

        count = len(open_windows)

        if count < 2:
            return {
                "success": False,
                "message": (
                    f"Only {count} usable open window(s) were found. "
                    "At least 2 are required for arrangement."
                )
            }

        if count > 4:
            return {
                "success": False,
                "message": (
                    f"Found {count} open windows. "
                    "Automatic arrangement currently supports "
                    "2 to 4 windows."
                ),
                "windows": [
                    window.title
                    for window in open_windows
                ]
            }

        # Automatically select layout
        if count == 2:
            layout = "two_columns"

        elif count == 3:
            layout = "three_columns"

        else:
            layout = "four_quarters"

        window_names = [
            window.title
            for window in open_windows
        ]

    except Exception as e:
        return {
            "success": False,
            "message": f"Could not inspect open windows: {e}"
        }

    # =========================================================
    # HITL MUST BE OUTSIDE try/except
    # =========================================================

    print("========== BEFORE INTERRUPT ==========")
    print("WINDOWS:", window_names)
    print("LAYOUT:", layout)

    decision = interrupt(
        f"Do you want to arrange "
        f"{', '.join(window_names)} using the {layout} layout?"
    )

    print("========== AFTER INTERRUPT ==========")
    print("DECISION:", decision)

    # =========================================================
    # Perform the actual action
    # =========================================================

    try:
        return _arrange_window_objects(
            windows=open_windows,
            layout=layout
        )

    except Exception as e:
        return {
            "success": False,
            "message": f"Could not arrange windows: {e}"
        }


@tool
def arrange_windows(applications: list[str]) -> dict:
    """
    Arrange the specific applications requested by the user.

    The applications must be currently open.

    The order of applications determines their position:

    2 applications:
        first  -> left
        second -> right

    3 applications:
        first  -> left
        second -> middle
        third  -> right

    4 applications:
        first  -> top-left
        second -> top-right
        third  -> bottom-left
        fourth -> bottom-right

    The layout is automatically selected based on the number
    of requested applications. The LLM must not provide a layout.
    """

    # ============================================================
    # 1. VALIDATE INPUT
    # ============================================================

    if not applications:
        return {
            "success": False,
            "message": "No applications were provided."
        }

    applications = [
        application.lower().strip()
        for application in applications
    ]

    applications = list(dict.fromkeys(applications))

    if len(applications) < 2:
        return {
            "success": False,
            "message": "At least two applications are required."
        }

    if len(applications) > 4:
        return {
            "success": False,
            "message": (
                "A maximum of 4 applications can be arranged "
                "at once."
            )
        }


    # ============================================================
    # 2. SELECT LAYOUT
    # ============================================================

    if len(applications) == 2:
        layout = "two_columns"

    elif len(applications) == 3:
        layout = "three_columns"

    else:
        layout = "four_quarters"


    # ============================================================
    # 3. FIND WINDOWS
    # ============================================================

    try:

        windows = []
        not_found = []

        for application in applications:

            if application not in APP_TITLES:
                not_found.append(application)
                continue

            window = None

            for title in APP_TITLES[application]:

                found_windows = gw.getWindowsWithTitle(title)

                if found_windows:
                    window = found_windows[0]
                    break

            if window is None:
                not_found.append(application)
                continue

            windows.append(window)

        if not_found:
            return {
                "success": False,
                "message": (
                    "Could not find the following requested "
                    f"open applications: {', '.join(not_found)}"
                ),
                "not_found": not_found
            }

        window_names = [
            window.title
            for window in windows
        ]

    except Exception as e:

        return {
            "success": False,
            "message": f"Could not find application windows: {e}"
        }


    # ============================================================
    # 4. HITL
    #
    # DO NOT PUT THIS INSIDE try/except Exception
    # ============================================================

    decision = interrupt(
        f"Do you want to arrange "
        f"{', '.join(window_names)} "
        f"using the {layout} layout?"
    )


    # ============================================================
    # 5. HANDLE USER RESPONSE
    # ============================================================

    if not decision:

        return {
            "success": False,
            "cancelled": True,
            "message": "Window arrangement cancelled by user."
        }


    # ============================================================
    # 6. ACTUAL WINDOW ARRANGEMENT
    # ============================================================

    try:

        return _arrange_window_objects(
            windows=windows,
            layout=layout
        )

    except Exception as e:

        return {
            "success": False,
            "message": f"Could not arrange windows: {e}"
        }
    


@tool
def setup_dev_environment() -> dict:
    """
    Start VS Code and Docker Desktop.
    If both applications start successfully, instruct Aegis to arrange
    VS Code on the left and Docker Desktop on the right using the
    two_columns layout.
    """

    try:
        # Start VS Code
        subprocess.Popen(["code"])

        # Start Docker Desktop
        docker_path = r"C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe"
        subprocess.Popen([docker_path])

        # Both launches succeeded.
        return {
            "success": True,
            "message": (
                "VS Code and Docker Desktop started successfully. "
                "You MUST now call arrange_windows with exactly these arguments: "
                'applications=["vscode", "docker"], '
                'layout="two_columns". '
                "Do not change the application order or layout."
            ),
            "next_tool": "arrange_windows",
            "next_tool_arguments": {
                "applications": ["vscode", "docker"],
                "layout": "two_columns"
            }
        }

    except FileNotFoundError as e:
        return {
            "success": False,
            "message": (
                f"Development environment setup failed because an application "
                f"could not be found: {e}. "
                "Do NOT call arrange_windows."
            )
        }

    except Exception as e:
        return {
            "success": False,
            "message": (
                f"Development environment setup failed: {e}. "
                "Do NOT call arrange_windows."
            )
        }