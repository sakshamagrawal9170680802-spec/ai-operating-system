from pathlib import Path
from langchain_core.tools import tool
import string


@tool
def find_file_by_name(file_name: str) -> dict:
    """
    Find files on the user's Windows computer by name.

    Searches all available drives and returns matching full paths.

    The search supports:
    - exact filenames
    - filenames without extensions
    - case-insensitive matching
    """

    file_name = file_name.strip()

    if not file_name:
        return {
            "success": False,
            "message": "File name cannot be empty."
        }

    # Remove accidental quotes
    file_name = file_name.strip("\"'")

    # Separate filename and extension
    requested_name = Path(file_name).stem.lower()
    requested_suffix = Path(file_name).suffix.lower()

    matches = []

    # ============================================================
    # Find all Windows drives
    # ============================================================

    drives = []

    for letter in string.ascii_uppercase:

        drive = Path(f"{letter}:/")

        if drive.exists():
            drives.append(drive)

    # ============================================================
    # Search every drive
    # ============================================================

    for drive in drives:

        try:

            for path in drive.rglob("*"):

                try:

                    if not path.is_file():
                        continue

                    actual_name = path.stem.lower()
                    actual_suffix = path.suffix.lower()

                    # ------------------------------------------------
                    # If user supplied extension:
                    # exact filename + extension
                    # ------------------------------------------------

                    if requested_suffix:

                        if (
                            actual_name == requested_name
                            and actual_suffix == requested_suffix
                        ):
                            matches.append(str(path.resolve()))

                    # ------------------------------------------------
                    # If user did NOT supply extension:
                    # match filename regardless of extension
                    # ------------------------------------------------

                    else:

                        if actual_name == requested_name:
                            matches.append(str(path.resolve()))

                except (PermissionError, OSError):
                    continue

        except (PermissionError, OSError):
            continue

    # ============================================================
    # No results
    # ============================================================

    if not matches:

        return {
            "success": False,
            "message": (
                f"No file matching '{file_name}' "
                "was found on the available drives."
            )
        }

    # Remove duplicates
    matches = list(dict.fromkeys(matches))

    return {
        "success": True,
        "file_name": file_name,
        "count": len(matches),
        "matches": matches
    }