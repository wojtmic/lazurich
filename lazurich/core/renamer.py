from pathlib import Path

from lazurich.core.paths import RENAMED
from lazurich.core.utils import get_os_name


def renamed(filename: str):
    return RENAMED / filename

def rename_file(src: Path, filename: str):
    link = RENAMED / filename
    link.parent.mkdir(parents=True, exist_ok=True)
    if link.is_symlink() or link.exists():
        return link
    if get_os_name() == "windows":
        src.copy(link)
    else:
        link.hardlink_to(src)
    return link