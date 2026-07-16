from lazurich.api.mojang import get_client_download
from lazurich.core.network import download_file
from lazurich.core.paths import WORKING
from lazurich.core.store import store_file, get_file


async def download_version_jar(ver: str):
    file = get_client_download(ver)

    check = await get_file(file)
    if check: return check

    await download_file(file, WORKING / 'client.jar')
    await store_file(WORKING / 'client.jar', file.checksum_type)

    return await get_file(file)

if __name__ == "__main__":
    import asyncio
    asyncio.run(download_version_jar("26.1.2"))
    