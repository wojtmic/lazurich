import httpx
from functools import lru_cache

BASE = 'https://meta.fabricmc.net/v2'

@lru_cache(maxsize=None)
def get_loader_versions(mc_ver: str):
    try:
        response = httpx.get(f'{BASE}/versions/loader/{mc_ver}')
        return response.json()
    except httpx.ConnectError:
        return 'Fabric meta API unreachable'

@lru_cache(maxsize=None)
def get_latest_loader_version(mc_ver: str) -> str:
    versions = get_loader_versions(mc_ver)
    return versions[0]['loader']['version']

@lru_cache(maxsize=None)
def get_loader_meta(mc_ver: str, loader_ver: str):
    try:
        response = httpx.get(f'{BASE}/versions/loader/{mc_ver}/{loader_ver}')
        return response.json()
    except httpx.ConnectError:
        return 'Fabric meta API unreachable'