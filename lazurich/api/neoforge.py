import httpx
import xml.etree.ElementTree as ET
from functools import lru_cache

from lazurich import get_client

BASE = 'https://maven.neoforged.net/releases/net/neoforged/neoforge'

@lru_cache(maxsize=None)
def get_all_versions() -> list[str]:
    try:
        response = httpx.get(f'{BASE}/maven-metadata.xml')
        root = ET.fromstring(response.text)
        return [v.text for v in root.findall('versioning/versions/version')]
    except httpx.ConnectError:
        return []

@lru_cache(maxsize=None)
def get_versions_for_mc(mc_ver: str) -> list[str]:
    parts = mc_ver.split('.')
    if len(parts) == 2:
        prefix = f'{parts[1]}.0.'
    else:
        prefix = f'{parts[1]}.{parts[2]}.'

    return [v for v in get_all_versions() if v.startswith(prefix)]

def _sort_key(version: str) -> tuple:
    numeric_part = version.split('-')[0]
    is_beta = '-' in version
    return (*(int(p) for p in numeric_part.split('.')), is_beta)

@lru_cache(maxsize=None)
def get_latest_version_for_mc(mc_ver: str) -> str | None:
    versions = get_versions_for_mc(mc_ver)
    if not versions:
        return None
    return max(versions, key=_sort_key)

def get_installer_url(neoforge_ver: str) -> str:
    return f'{BASE}/{neoforge_ver}/neoforge-{neoforge_ver}-installer.jar'

async def download_installer(neoforge_ver: str, dest) -> None:
    url = get_installer_url(neoforge_ver)
    async with get_client().stream('GET', url) as response:
        response.raise_for_status()
        with open(dest, 'wb') as f:
            async for chunk in response.aiter_bytes():
                f.write(chunk)


async def main():
    ver = get_latest_version_for_mc('1.21.1')
    print(f'downloading {ver}')
    await download_installer(ver, 'neoforge-installer.jar')

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())