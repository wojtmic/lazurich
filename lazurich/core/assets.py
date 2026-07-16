from lazurich.core.models.general import DownloadItem, ChecksumEnum
from lazurich.core.network import download_batch
from lazurich.api.mojang import get_asset_manifest, get_for_version
from lazurich.core.paths import ASSETS
import json

async def download_version_assets(version: str):
    manifest = get_asset_manifest(version)
    downloads = []

    for asset in manifest['objects'].values():
        link = f'https://resources.download.minecraft.net/{asset['hash'][:2]}/{asset['hash']}'
        path = ASSETS / 'objects' / asset['hash'][:2] / asset['hash']

        if path.exists(): continue

        item = DownloadItem(link=link, checksum_type=ChecksumEnum.SHA1, checksum=asset['hash'])

        path.parent.mkdir(exist_ok=True, parents=True)
        downloads.append((item, path))

    await download_batch(downloads)

async def download_version_manifest(version: str):
    manifest = get_asset_manifest(version)
    ver_data = get_for_version(version)

    path = ASSETS / 'indexes' / f'{ver_data['assetIndex']['id']}.json'
    path.parent.mkdir(exist_ok=True, parents=True)

    with open(path, 'w') as f:
        f.write(json.dumps(manifest))

if __name__ == "__main__":
    import asyncio
    asyncio.run(download_version_assets('26.1.2'))
    asyncio.run(download_version_manifest('26.1.2'))
