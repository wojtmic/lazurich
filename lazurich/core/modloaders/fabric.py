import os
from functools import lru_cache
from pathlib import Path
from shutil import rmtree

import httpx
from loguru import logger

from lazurich.api import fabric
from lazurich.core.models.general import DownloadItem, ChecksumEnum
from lazurich.core.network import download_batch, download_file
from lazurich.core.paths import WORKING
from lazurich.core.store import check_file_stored, store_file, get_file_path


@lru_cache(maxsize=None)
def maven_path(name: str) -> str:
    group, artifact, version = name.split(':')
    return f"{group.replace('.', '/')}/{artifact}/{version}/{artifact}-{version}.jar"

@lru_cache(maxsize=None)
def make_fabric_downloads(mc_ver: str, loader_ver: str) -> list[DownloadItem]:
    meta = fabric.get_loader_meta(mc_ver, loader_ver)
    libs = meta['launcherMeta']['libraries']
    all_libs = libs.get('common', []) + libs.get('client', [])
    l = [
        DownloadItem(lib['sha1'], ChecksumEnum.SHA1, lib['url'].rstrip('/') + '/' + maven_path(lib['name']))
        for lib in all_libs
    ]
    l.append(get_fabric_download(loader_ver))
    l.append(get_fabric_intermediary_download(mc_ver))
    return l

async def download_fabric(mc_ver: str, loader_ver: str):
    items = make_fabric_downloads(mc_ver, loader_ver)
    p = (WORKING / 'fabric')
    if p.exists(): rmtree(p)
    p.mkdir(parents=True, exist_ok=True)

    downloads = [(i, Path(WORKING / 'fabric' / i.checksum)) for i in items if not check_file_stored(i)]

    if not downloads:
        logger.info(f'All Fabric files for {mc_ver}:{loader_ver} already downloaded!')
        return
    else:
        logger.info(f'Downloading {len(downloads)} native(s) for {mc_ver}:{loader_ver}')

    await download_batch(downloads)

    map = {i.checksum: i.link.split('/')[-1] for i in items}
    for i in p.iterdir():
        await store_file(i, ChecksumEnum.SHA1, map[str(i.name)])

    rmtree(p)

def get_fabric_str(mc_ver: str, loader_ver: str) -> str:
    items = make_fabric_downloads(mc_ver, loader_ver)
    return os.pathsep.join(
        str(get_file_path(i)) for i in items
    )

def get_fabric_download(loader_ver: str) -> DownloadItem:
    checksum = httpx.get(f'https://maven.fabricmc.net/net/fabricmc/fabric-loader/{loader_ver}/fabric-loader-{loader_ver}.jar.sha1').content.decode()

    item = DownloadItem(
        checksum=checksum,
        checksum_type=ChecksumEnum.SHA1,
        link=f'https://maven.fabricmc.net/net/fabricmc/fabric-loader/{loader_ver}/fabric-loader-{loader_ver}.jar'
    )

    return item

def get_fabric_intermediary_download(mc_ver: str) -> DownloadItem:
    checksum = httpx.get(f'https://maven.fabricmc.net/net/fabricmc/intermediary/{mc_ver}/intermediary-{mc_ver}.jar.sha1').content.decode()

    item = DownloadItem(
        checksum=checksum,
        checksum_type=ChecksumEnum.SHA1,
        link=f'https://maven.fabricmc.net/net/fabricmc/intermediary/{mc_ver}/intermediary-{mc_ver}.jar'
    )

    return item

async def download_fabric_jar(loader_ver: str):
    file = get_fabric_download(loader_ver)

    path = get_file_path(file)
    if path.exists(): return path

    WORKING.mkdir(parents=True, exist_ok=True)
    await download_file(file, WORKING / 'fabric.jar')
    await store_file(WORKING / 'fabric.jar', file.checksum_type, f'fabric-{loader_ver}.jar')

    return path

if __name__ == "__main__":
    from lazurich.api.fabric import get_latest_loader_version
    import asyncio
    # print(get_latest_loader_version('1.21.1'))
    print(get_fabric_download(get_latest_loader_version('1.21.1')))
    # print(make_fabric_downloads('1.21.1', get_latest_loader_version('1.21.1')))
    # asyncio.run(download_fabric('1.21.1', get_latest_loader_version('1.21.1')))
