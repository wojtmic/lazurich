import os
import httpx
import asyncio
import aiofiles
import aiofiles.os
import json

JAR_STORAGE   = os.path.expanduser('~/.local/share/lazurich/jars')
ASSET_STORAGE = os.path.expanduser('~/.local/share/lazurich/assets')
LIB_STORAGE   = os.path.expanduser('~/.local/share/lazurich/libs')
NATIVE_STORAGE= os.path.expanduser('~/.local/share/lazurich/natives')

with open(os.path.expanduser('~/.local/share/lazurich/accounts.json')) as f:
    content = f.read()
    loads = json.loads(content)
    OWNS_MC = loads['ownsMinecraft']

os.makedirs(JAR_STORAGE,   exist_ok=True)
os.makedirs(ASSET_STORAGE, exist_ok=True)
os.makedirs(LIB_STORAGE,   exist_ok=True)
os.makedirs(NATIVE_STORAGE,exist_ok=True)

async def download_worker_assets(session: httpx.AsyncClient, semaphore: asyncio.Semaphore, url: str, file_hash: str):
    async with semaphore:
        print(f'[START] Downloading {url}')

        try:
            response = await session.get(url, timeout=10)
            response.raise_for_status()

            content = await response.aread()

            print(f'[DOWNLOADED] {url}')

            basedir = os.path.join(ASSET_STORAGE, 'objects', file_hash[:2])
            await aiofiles.os.makedirs(basedir, exist_ok=True)

            async with aiofiles.open(os.path.join(basedir, file_hash), 'wb') as f:
                await f.write(content)

        except httpx.ConnectError:
            print(f'[FAILED] to download {url}, Mojang servers likely unreachable')

async def download_worker_lib(session: httpx.AsyncClient, semaphore: asyncio.Semaphore, url: str):
    async with semaphore:
        print(f'[START] Downloading {url}')

        try:
            response = await session.get(url, timeout=10)
            response.raise_for_status()

            content = await response.aread()

            print(f'[DOWNLOADED] {url} ({url.split('/')[-1]})')

            filepath = os.path.join(LIB_STORAGE, url.split('/')[-1])

            async with aiofiles.open(filepath, 'wb') as f:
                await f.write(content)

        except httpx.ConnectError:
            print(f'[FAILED] to download {url}, Mojang servers likely unreachable')

def download_version_jar(version: dict, client: bool = True):
    if not OWNS_MC: raise PermissionError('User does not own Minecraft!') # Temporarily use PermissionError until custom exceptions are implemented

    if client: url = version['downloads']['client']['url']
    else: url = version['downloads']['server']['url']

    if client: filename = f'{version['id']}-client.jar'
    else: filename = f'{version['id']}-server.jar'

    with httpx.Client(timeout=None) as client:
        with client.stream('GET', url) as response:
            response.raise_for_status()

            with open(os.path.join(JAR_STORAGE, filename), 'wb') as f:
                for chunk in response.iter_bytes(chunk_size=8192):
                    f.write(chunk)

async def download_version_assets(assetManifest: dict, version: str):
    if not OWNS_MC: raise PermissionError('User does not own Minecraft!')  # Temporarily use PermissionError until custom exceptions are implemented
    semaphore = asyncio.Semaphore(15)

    with open(os.path.join(ASSET_STORAGE, 'indexes', f'{version}.json'), 'w') as f:
        f.write(json.dumps(assetManifest))

    async with httpx.AsyncClient() as client:
        tasks = []
        for asset in assetManifest['objects']:
            a = assetManifest['objects'][asset]

            tasks.append(
                download_worker_assets(
                    client,
                    semaphore,
                    f'https://resources.download.minecraft.net/{a['hash'][:2]}/{a['hash']}',
                    a['hash']
                )
            )

        print(f'Downloading assets ({len(assetManifest['objects'])})')
        await asyncio.gather(*tasks)
        print('Finished downloading assets!')

async def download_version_libs(version: dict):
    if not OWNS_MC: raise PermissionError('User does not own Minecraft!')  # Temporarily use PermissionError until custom exceptions are implemented
    libs = version['libraries']

    semaphore = asyncio.Semaphore(10)

    async with httpx.AsyncClient() as client:
        tasks = []
        for asset in libs:
            tasks.append(
                download_worker_lib(
                    client,
                    semaphore,
                    asset['downloads']['artifact']['url'],
                    asset['downloads']['artifact']['sha1']
                )
            )

        print(f'Downloading libs ({len(libs)})')
        await asyncio.gather(*tasks)
        print('Finished downloading libs!')
