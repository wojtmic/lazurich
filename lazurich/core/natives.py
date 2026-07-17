import zipfile
from functools import lru_cache
from pathlib import Path
from shutil import rmtree

from loguru import logger

from lazurich.api.mojang import get_for_version
from lazurich.core.paths import WORKING, NATIVES
from lazurich.core.store import store_file, check_file_stored, get_file_path
from lazurich.core.utils import get_arch, get_os_name
from lazurich.core.models.general import DownloadItem, ChecksumEnum
from lazurich.core.network import download_batch

@lru_cache(maxsize=None)
def get_natives_for_version(ver: str):
    libs = []
    for lib in get_for_version(ver)['libraries']:
        if not lib.get('rules'):
            libs.append(lib)
            continue

        os_name = get_os_name()
        arch = get_arch()

        allowed = False
        for rule in lib['rules']:
            action = rule['action']
            os_rule = rule.get('os')

            if os_rule is None:
                match = True
            else:
                match = True
                if 'name' in os_rule and os_rule['name'] != os_name:
                    match = False
                if 'arch' in os_rule and os_rule['arch'] != arch:
                    match = False

            if match:
                allowed = (action == 'allow')

        if allowed:
            libs.append(lib)

    return libs

@lru_cache(maxsize=None)
def make_natives_downloads(ver: str) -> list[DownloadItem]:
    return [DownloadItem(i['downloads']['artifact']['sha1'], ChecksumEnum.SHA1, i['downloads']['artifact']['url']) for i in get_natives_for_version(ver)]

async def download_natives(ver: str):
    items = make_natives_downloads(ver)
    p = (WORKING / 'natives')
    if p.exists(): rmtree(p)
    p.mkdir(parents=True, exist_ok=True)

    downloads = [(i, Path(WORKING / 'natives' / i.checksum)) for i in items if not check_file_stored(i)]


    if not downloads:
        logger.info(f'All natives for {ver} already downloaded!')
        return
    else:
        logger.info(f'Downloading {len(downloads)} native(s) for {ver}')

    await download_batch(downloads)

    map = {i.checksum: i.link.split('/')[-1] for i in items}
    for i in p.iterdir():
        await store_file(i, ChecksumEnum.SHA1, map[str(i.name)])

def extract_natives(ver: str):
    items = make_natives_downloads(ver)
    p = NATIVES / ver
    p.mkdir(exist_ok=True, parents=True)

    for i in items:
        path = get_file_path(i)
        name = i.link.split('/')[-1]
        if not 'native' in name: continue

        with zipfile.ZipFile(path) as zf:
            for member in zf.infolist():
                if not member.filename.endswith(('.so', '.dylib', '.dll')): continue
                target_name = Path(member.filename).name
                with zf.open(member) as src, open(p / target_name, "wb") as out:
                    logger.debug(f'Extracting {target_name}...')
                    out.write(src.read())

def get_libs_str(ver: str) -> str:
    return ':'.join(str(get_file_path(i)) for i in make_natives_downloads(ver) if not 'native' in i.link)

if __name__ == "__main__":
    # import asyncio
    # asyncio.run(download_natives('26.1.2'))
    extract_natives('26.1.2')
