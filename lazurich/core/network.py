import asyncio
import hashlib
from pathlib import Path
from typing import List
import anyio
import httpx
from lazurich import get_client
from lazurich.core.models.general import DownloadItem

client = get_client()

class DownloadError(Exception):
    """Custom exception for download failures."""
    pass

class ChecksumError(DownloadError):
    """Raised when the downloaded file checksum does not match."""
    pass

async def download_file(item: DownloadItem, path: Path, chunk_size: int = 8192):
    hasher = hashlib.new(item.checksum_type)

    try:
        async with client.stream("GET", item.link, follow_redirects=True) as response:
            response.raise_for_status()

            async def write_chunks():
                async with await anyio.open_file(path, "wb") as f:
                    async for chunk in response.aiter_bytes(chunk_size=chunk_size):
                        hasher.update(chunk)
                        await f.write(chunk)

            await write_chunks()

        calculated_checksum = hasher.hexdigest()
        if calculated_checksum != item.checksum:
            await anyio.Path(path).unlink(missing_ok=True)
            raise ChecksumError(
                f"Checksum mismatch for {item.link}. Expected {item.checksum}, got {calculated_checksum}"
            )

    except (httpx.HTTPError, OSError) as e:
        raise DownloadError(f"Error downloading {item.link}: {e}") from e

async def download_batch(items: List[tuple[DownloadItem, Path]], concurrency_limit: int = 20):
    """
    Downloads multiple files in parallel.
    """
    semaphore = asyncio.Semaphore(concurrency_limit)

    async def _sem_task(item: DownloadItem, path: Path):
        async with semaphore:
            await download_file(item, path)

    async with asyncio.TaskGroup() as tg:
        for item, dest in items:
            tg.create_task(_sem_task(item, dest))
