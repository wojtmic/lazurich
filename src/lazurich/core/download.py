import asyncio
import hashlib
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from loguru import logger

from lazurich.core.network import client

c = client()


class ChecksumType(StrEnum):
    SHA1 = 'sha1'
    SHA256 = 'sha256'
    SHA512 = 'sha512'
    MD5 = 'md5'

@dataclass
class File:
    url: str
    path: Path

    checksum: str | None
    checksum_type: ChecksumType | None

def can_download(file: File) -> bool:
    if not file.path.exists():
        return True
    if file.checksum_type is None:
        return False
    h = hashlib.new(file.checksum_type.value)
    with open(file.path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest() != file.checksum

async def download_file(file: File, verify_checksum: bool = True):
    if not can_download(file): return

    logger.debug(f'Downloading {file.url} to {file.path} ({file.checksum})')

    file.path.parent.mkdir(parents=True, exist_ok=True)
    if file.checksum_type is None: verify_checksum = False

    part = file.path.with_name(file.path.name + ".part")
    async with c.stream('GET', file.url) as resp:
        resp.raise_for_status()
        if verify_checksum: h = hashlib.new(file.checksum_type.value)
        with open(part, 'wb') as f: # noqa: ASYNC230, handoff might slow it down a tiny bit so we're using the sync open() here
            async for chunk in resp.aiter_bytes():
                if verify_checksum: h.update(chunk)
                f.write(chunk)
    
    if verify_checksum and h.hexdigest() != file.checksum:
        part.unlink()
        raise Exception('Checksum invalid') # TODO: use custom exception

    part.replace(file.path)
    logger.debug(f'Downloaded {file.url} into {file.path}')

async def download_files(files: list[File], verify_checksum: bool = True, concurrency: int = 16):
    sem = asyncio.Semaphore(concurrency)

    async def worker(file: File):
        async with sem:
            await download_file(file, verify_checksum)

    async with asyncio.TaskGroup() as tg:
        for f in files:
            tg.create_task(worker(f))
