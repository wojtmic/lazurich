from pathlib import Path

from lazurich.api.microsoft import get_msa_token, do_full_auth
from lazurich.core.assets import download_version_manifest, download_version_assets
from lazurich.core.instances import create_instance, fill_instance
from lazurich.core.jars import download_version_jar
from lazurich.core.launcher import launch_game
from lazurich.core.models.general import Instance, ModloaderEnum
from lazurich.core.modloaders.fabric import download_fabric, download_intermediary_jar
from lazurich.core.natives import download_natives, extract_natives
from lazurich.core.paths import INSTANCES

async def main():
    await download_version_assets('1.21.1')
    await download_version_manifest('1.21.1')
    await download_natives('1.21.1')
    extract_natives('1.21.1')
    await download_version_jar('1.21.1')

    await download_fabric('1.21.1', '0.19.3')
    await download_intermediary_jar('1.21.1')

    # inst = Instance(name='ULTRA epic instanance (fabric)', version='1.21.1', modloader=ModloaderEnum.FABRIC, modloader_version='0.19.3')
    # instance_id = await create_instance(inst)
    # fill_instance(instance_id)

    # msa = get_msa_token()
    # prof, token = await do_full_auth(msa)
    # launch_game('1.21.1', INSTANCES / instance_id / '.minecraft', prof, token, loader=ModloaderEnum.FABRIC, loader_ver='0.19.3')

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
