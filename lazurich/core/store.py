from lazurich.core.models.general import DownloadItem
from lazurich.core.paths import STORE
from lazurich.core.network import download_file, download_batch

def get_file_path(item: DownloadItem):
    return STORE / item.checksum_type.lower() / item.checksum[:2] / item.checksum

def check_file_stored(item: DownloadItem):
    return (get_file_path(item)).exists()

async def get_file(item: DownloadItem):
    path = get_file_path(item)
    if path.exists(): return path

    path.parent.mkdir(exist_ok=True)
    await download_file(item=item, path=path)

    return path

async def get_files(items: list[DownloadItem]):
    stored = [obj for obj in items if check_file_stored(obj)]
    missing = set(items) - set(stored)

    pairs = [(item, get_file_path(item)) for item in missing]
    await download_batch(pairs)

    paths = [get_file_path(item) for item in items]

    return paths
