import psutil

#kill pid protection
PROTECTED_EXECUTABLES = {
    "system",
    "system idle process",
    "registry",
    "smss.exe",
    "csrss.exe",
    "wininit.exe",
    "winlogon.exe",
    "services.exe",
    "lsass.exe",
    "svchost.exe",
    "explorer.exe",
    "dwm.exe",
    "fontdrvhost.exe",
    "sihost.exe",
    "ctfmon.exe",
}
PROTECTED_PIDS = {0, 1, 2, 3, 4}
def is_executable_protected(pid:int)->tuple[bool,str]:

    if(pid in PROTECTED_PIDS):
        return True, f"PID {pid} is protected."

    try:
        process=psutil.Process(pid)
        name=process.name()

        if(name.lower() in PROTECTED_EXECUTABLES):
            return True,f"Process '{name}' is protected."

        return False, f"Process '{name}' is not protected."

    except psutil.NoSuchProcess:
        return True, f"No process exists with PID {pid}."

    except psutil.AccessDenied:
        return True, f"Access denied when inspecting PID {pid}."

    except Exception as e:
        return True, f"ERROR occured when inspecting PID {pid} : {str(e)}."