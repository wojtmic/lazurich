import asyncio
import json

from lazurich.core.cache.mojang import Version
from lazurich.core.download import ChecksumType, File, download_file, download_files
from lazurich.core.paths import DATA_ROOT

LIBS = DATA_ROOT / 'libraries'
ASSETS = DATA_ROOT / 'assets'
RESOURCES = 'https://resources.download.minecraft.net/'
SHA1 = ChecksumType.SHA1

async def download_version(vid: str):
    v = Version.get_by_id(vid)
    files = [File(lib.url, LIBS / lib.path, lib.sha1, SHA1) for lib in v.libraries]

    ai = v.asset_index
    index = ASSETS / 'indexes' / f'{ai.id}.json'
    await download_file(File(ai.url, index, ai.sha1, SHA1))

    hashes = {o['hash'] for o in json.loads(index.read_text())['objects'].values()}
    files += [File(f'{RESOURCES}{h[:2]}/{h}', ASSETS / 'objects' / h[:2] / h, h, SHA1) for h in hashes]

    await download_files(files)

if __name__ == '__main__':
    from lazurich.core import network
    from lazurich.core.cache.db import init_db

    init_db()

    async def run():
        try:
            await download_version('26.1.2')
        finally:
            await network.close()

    asyncio.run(run())