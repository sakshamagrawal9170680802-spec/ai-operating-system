import comtypes
from pycaw.pycaw import AudioUtilities
from langchain_core.tools import tool
from langgraph.types import interrupt

@tool
def get_default_audio_device()->dict:
    """
    Get the current default audio output device.
    """

    try:
        comtypes.CoInitialize()


        device=AudioUtilities.GetSpeakers()

        return {
                "name": device.FriendlyName,
                "id": device.id,
                "state": device.state.name
            }
    except Exception as e:
            return {
                    "error": f"Failed to get current default audio device: {str(e)}"
                }
    finally:
        comtypes.CoUninitialize()
            

    
    


@tool
def list_audio_output_devices() -> list[dict]:
    """
    List all audio output devices connected to the computer
    and identify the current default output device.

    Returns:
        A list containing each audio output device, its name,
        ID, state, and whether it is the current default device.
    """

    try:
        comtypes.CoInitialize()
        devices = AudioUtilities.GetAllDevices()#all audio output device
        default_device = AudioUtilities.GetSpeakers()#current default device

        default_id = default_device.id

        audio_devices = []

        for device in devices:
            # Ignore input devices
            if device.id.startswith("{0.0.1."):
                continue

            audio_devices.append({
                "name": device.FriendlyName,
                "id": device.id,
                "state": device.state.name,
                "is_default": device.id == default_id,
            })

        return audio_devices

    except Exception as e:
        return [
            {
                "error": f"Failed to list audio devices: {str(e)}"
            }
        ]
    finally:
        comtypes.CoUninitialize()


@tool
def get_volume() -> dict:
    """
    Get the current volume level of the default audio output device.

    Returns:
        The current volume percentage and device name.
    """
    try:
        comtypes.CoInitialize()

        device = AudioUtilities.GetSpeakers()
        volume = device.EndpointVolume

        current_volume = volume.GetMasterVolumeLevelScalar() * 100

        return {
            "success": True,
            "device": device.FriendlyName,
            "volume": round(current_volume, 1),
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to get volume: {str(e)}"
        }

    finally:
        comtypes.CoUninitialize()


@tool
def set_volume(level: int) -> dict:
    """
    Set the volume of the default audio output device.

    Args:
        level: Desired volume percentage from 0 to 100.

    Returns:
        The new volume level and device name.
    """

    if level<0 or level>100:
        return {
            "success": False,
            "message": "Volume must be between 0 and 100."
        }

    decision = interrupt(f"Do you want to set the system volume to {level}%?")
    if not decision:
        return {
            "success": False,
            "cancelled": True,
            "message": "Volume change cancelled by user."
        }
    
    try:
        comtypes.CoInitialize()

        device = AudioUtilities.GetSpeakers()
        volume = device.EndpointVolume

        volume.SetMasterVolumeLevelScalar(level / 100, None)

        return {
            "success": True,
            "device": device.FriendlyName,
            "volume": level,
            "message": f"Volume set to {level}%."
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to set volume: {str(e)}"
        }

    finally:
        comtypes.CoUninitialize()


@tool
def get_mute_status() -> dict:
    """
    Check whether the default audio output device is currently muted.

    Returns:
        The mute status and device name.
    """

    try:
        comtypes.CoInitialize()

        device = AudioUtilities.GetSpeakers()
        volume = device.EndpointVolume

        muted = bool(volume.GetMute())

        return {
            "success": True,
            "device": device.FriendlyName,
            "muted": muted,
            "status": "Muted" if muted else "Not muted"
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to get mute status: {str(e)}"
        }

    finally:
        comtypes.CoUninitialize()


@tool
def mute() -> dict:
    """
    Mute the default audio output device.
    """

    decision = interrupt("Do you want to mute the system audio?")
    if not decision:
        return {
            "success": False,
            "cancelled": True,
            "message": "Mute operation cancelled by user."
        }
    try:
        comtypes.CoInitialize()

        device = AudioUtilities.GetSpeakers()
        volume = device.EndpointVolume

        volume.SetMute(1, None)

        return {
            "success": True,
            "device": device.FriendlyName,
            "muted": True,
            "message": "Audio muted."
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to mute audio: {str(e)}"
        }

    finally:
        comtypes.CoUninitialize()


@tool
def unmute() -> dict:
    """
    Unmute the default audio output device.
    """

    decision = interrupt("Do you want to unmute the system audio?")

    if not decision:
        return {
            "success": False,
            "cancelled": True,
            "message": "Unmute operation cancelled by user."
        }
    try:
        comtypes.CoInitialize()

        device = AudioUtilities.GetSpeakers()
        volume = device.EndpointVolume

        volume.SetMute(0, None)

        return {
            "success": True,
            "device": device.FriendlyName,
            "muted": False,
            "message": "Audio unmuted."
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to unmute audio: {str(e)}"
        }

    finally:
        comtypes.CoUninitialize()
