import platform

def os_string() -> str:
    system = platform.system()
    if system == "Linux":
        try:
            name = platform.freedesktop_os_release().get("PRETTY_NAME", "Linux")
        except OSError:
            name = "Linux"
        os_part = f"{name} (kernel {platform.release()})"
    elif system == "Darwin":
        os_part = f"macOS {platform.mac_ver()[0]}"
    elif system == "Windows":
        os_part = f"Windows {platform.release()} ({platform.version()})"
    else:
        os_part = platform.platform()

    impl = platform.python_implementation()
    if impl != 'CPython': impl += " (!)"
    return f"{os_part} {platform.machine()}, {impl} {platform.python_version()}"
