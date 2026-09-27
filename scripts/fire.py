import asyncio

from lazurich.core.models.general import DownloadItem, ChecksumEnum
from lazurich.core.network import download_file
from lazurich.core.paths import WORKING


async def main():
    i = DownloadItem(
        link='https://cdn.modrinth.com/data/LsX4agNw/versions/d557eTKW/end_stuff-1.7.2-1.20.1.jar',
        checksum='739a964719da9ee55f03a0611c0af0756d4103fa',
        checksum_type=ChecksumEnum.SHA1
    )

    WORKING.mkdir(parents=True, exist_ok=True)
    await download_file(i, WORKING / 'enderimprovementer.jar')

if __name__ == "__main__":
    asyncio.run(main())
