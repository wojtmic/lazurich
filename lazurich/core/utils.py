import random
import string
import platform

_ALPHABET = string.ascii_lowercase + string.digits

def gen_id() -> str:
    return ''.join(random.choices(_ALPHABET, k=8))

def get_os_name() -> str:
    system = platform.system().lower()
    if "windows" in system:
        return "windows"
    elif "darwin" in system:
        return "osx"
    else:
        return "linux"

def get_arch() -> str:
    machine = platform.machine().lower()
    if machine in ("arm64", "aarch64"):
        return "arm64"
    elif machine in ("x86", "i386", "i686"):
        return "x86"
    else:
        return "x64"  # x86_64, amd64
