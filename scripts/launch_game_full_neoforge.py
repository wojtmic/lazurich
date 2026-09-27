from pathlib import Path

from lazurich.api.microsoft import get_msa_token, do_full_auth
from lazurich.api.neoforge import get_latest_version_for_mc
from lazurich.core.assets import download_version_manifest, download_version_assets
from lazurich.core.instances import create_instance, fill_instance
from lazurich.core.jars import download_version_jar
from lazurich.core.launcher import launch_game
from lazurich.core.models.general import Instance, ModloaderEnum
from lazurich.core.modloaders.neoforge import install_neoforge
from lazurich.core.natives import download_natives, extract_natives
from lazurich.core.paths import INSTANCES

MC_VER = '1.21.1'
NF_VER = '21.1.233'

async def main():
    await download_version_assets(MC_VER)
    await download_version_manifest(MC_VER)
    await download_natives(MC_VER)
    extract_natives(MC_VER)
    await download_version_jar(MC_VER)

    # downloads NeoForge's libraries + processor tools, then runs the installer
    # processors to produce the patched client jar
    await install_neoforge(MC_VER, NF_VER)

    inst = Instance(name='ULTRA epic instanance (neoforge)', version=MC_VER, modloader=ModloaderEnum.NEOFORGE, modloader_version=NF_VER)
    instance_id = await create_instance(inst)
    fill_instance(instance_id)

    msa = get_msa_token()
    prof, token = await do_full_auth(msa)
    proc = launch_game(MC_VER, INSTANCES / instance_id / '.minecraft', prof, token, loader=ModloaderEnum.NEOFORGE, loader_ver=NF_VER)
    proc.wait()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())