from pathlib import Path
import hashlib
import aiofiles
import shutil
import dbm

from lazurich.core.models.general import DownloadItem, ChecksumEnum
from lazurich.core.paths import STORE
from lazurich.core.network import download_file, download_batch

async def store_file(src: Path, checksum_type: ChecksumEnum, name: str = None) -> None:
    if not name: name = src.name

    hasher = hashlib.new(checksum_type.lower())
    async with aiofiles.open(src, "rb") as f:
        while chunk := await f.read(65536):
            hasher.update(chunk)
    checksum = hasher.hexdigest()

    path = STORE / checksum_type.lower() / checksum[:2] / checksum
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, path)

    with dbm.open(str(STORE / checksum_type / 'index'), 'c') as db:
        db[checksum] = name

    with dbm.open(str(STORE / checksum_type / 'reverse_index'), 'c') as rdb:
        rdb[name] = checksum

def get_file_by_known_name(name: str, checksum_type: ChecksumEnum):
    with dbm.open(STORE / checksum_type / 'reverse_index', 'r') as db:
        checksum = db[name]
        return get_file_path(DownloadItem(
            checksum=checksum.decode(),
            checksum_type=checksum_type,
            link='fake://url'
        ))

def get_file_path(item: DownloadItem):
    return STORE / item.checksum_type.lower() / item.checksum[:2] / item.checksum

def check_file_stored(item: DownloadItem):
    return (get_file_path(item)).exists()

async def get_file_or_download(item: DownloadItem):
    path = get_file_path(item)
    if path.exists(): return path

    path.parent.mkdir(exist_ok=True, parents=True)
    await download_file(item=item, path=path)

    return path

async def get_files(items: list[DownloadItem]):
    stored = [obj for obj in items if check_file_stored(obj)]
    missing = set(items) - set(stored)

    pairs = [(item, get_file_path(item)) for item in missing]
    await download_batch(pairs)

    paths = [get_file_path(item) for item in items]

    return paths
