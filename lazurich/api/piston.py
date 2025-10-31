import httpx
from functools import lru_cache

@lru_cache(maxsize=None)
def get_manifest():
    try:
        response = httpx.get('https://piston-meta.mojang.com/mc/game/version_manifest_v2.json')
        data = response.json()
        return data
    except httpx.ConnectError:
        return 'Piston API unreachable'

@lru_cache(maxsize=None)
def get_for_version(id: str):
    manifest = get_manifest()
    obj = next(
        (item for item in manifest['versions'] if item['id'] == id),
        None
    )
    if obj is None: return None

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

if __name__ == '__main__':
    print(get_for_version('1.21.1'))
