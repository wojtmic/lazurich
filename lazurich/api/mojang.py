import httpx
from functools import lru_cache
from lazurich.core.models.general import DownloadItem, ChecksumEnum
from lazurich.core.store import get_file

@lru_cache(maxsize=None)
def get_manifest():
    try:
        response = httpx.get('https://piston-meta.mojang.com/mc/game/version_manifest_v2.json')
        data = response.json()
        return data
    except httpx.ConnectError:
        return 'Piston API unreachable'

@lru_cache(maxsize=None)
def get_latest():
    manifest = get_manifest()
    return manifest['latest']

@lru_cache(maxsize=None)
def get_versions():
    manifest = get_manifest()
    return manifest['versions']

@lru_cache(maxsize=None)
def get_for_version(id: str):
    manifest = get_manifest()
    obj = next(
        (item for item in manifest['versions'] if item['id'] == id),
        None
    )
    if obj is None: raise Exception('BAD VERSION! TODO: CUSTOM EXCEPTION') # TODO: CUSTOM EXCEPTION

    try:
        response = httpx.get(obj['url'])
        data = response.json()
    except httpx.ConnectError:
        return 'Piston API unreachable'

    return data

@lru_cache(maxsize=None)
def get_asset_manifest(version_id: str):
    manifest = get_for_version(version_id)
    if manifest is None or manifest == 'Piston API unreachable':
        return manifest

    try:
        response = httpx.get(manifest['assetIndex']['url'])
        data = response.json()
    except httpx.ConnectError:
        return 'Piston API unreachable'

    return data

@lru_cache(maxsize=None)
def get_client_download(version_id: str):
    manifest = get_for_version(version_id)
    download = manifest['downloads']['client']
    item = DownloadItem(checksum=download['sha1'], checksum_type=ChecksumEnum.SHA1, link=download['url'])
    return item

if __name__ == '__main__':
    # print(get_versions())
    from lazurich.core.network import download_file
    from httpx import AsyncClient
    import asyncio
    from pathlib import Path

    item = get_client_download('1.21.9')
    print(item)

    print(get_file(item=item))
