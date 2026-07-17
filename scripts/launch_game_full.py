from pathlib import Path

from lazurich.api.microsoft import get_msa_token, do_full_auth
from lazurich.core.assets import download_version_manifest, download_version_assets
from lazurich.core.instances import create_instance, fill_instance
from lazurich.core.jars import download_version_jar
from lazurich.core.launcher import launch_game
from lazurich.core.models.general import Instance, ModloaderEnum
from lazurich.core.natives import download_natives, extract_natives
from lazurich.core.paths import INSTANCES

if __name__ == "__main__":
    import asyncio
    asyncio.run(download_version_assets('26.1.2'))
    asyncio.run(download_version_manifest('26.1.2'))

    asyncio.run(download_natives('26.1.2'))
    extract_natives('26.1.2')

    asyncio.run(download_version_jar("26.1.2"))

    inst = Instance(
        name='epic instnace',
        version='26.1.2',
        modloader=ModloaderEnum.VANILLA,
        modloader_version=''
    )
    import asyncio
    id = asyncio.run(create_instance(inst))
    fill_instance(id)

    msa = get_msa_token()
    prof, token = asyncio.run(do_full_auth(msa))
    launch_game('26.1.2', INSTANCES / id / '.minecraft', prof, token)
