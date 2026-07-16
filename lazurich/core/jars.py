from lazurich.api.mojang import get_client_download
from lazurich.core.network import download_file
from lazurich.core.paths import WORKING
from lazurich.core.store import store_file, get_file_path


async def download_version_jar(ver: str):
    file = get_client_download(ver)

    path = get_file_path(file)
    if path.exists(): return path

    WORKING.mkdir(parents=True, exist_ok=True)
    await download_file(file, WORKING / 'client.jar')
    await store_file(WORKING / 'client.jar', file.checksum_type, f'client-{ver}.jar')

    return path

if __name__ == "__main__":
    import asyncio
    asyncio.run(download_version_jar("26.1.2"))
    