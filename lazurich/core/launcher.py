import subprocess
from pathlib import Path
import os
from loguru import logger

from lazurich.api.microsoft import do_full_auth, get_msa_token
from lazurich.api.mojang import get_for_version
from lazurich.core.models.general import ChecksumEnum, ModloaderEnum
from lazurich.core.modloaders.fabric import get_fabric_str
from lazurich.core.natives import get_libs_str
from lazurich.core.paths import NATIVES, ASSETS
from lazurich.core.renamer import renamed, rename_file
from lazurich.core.store import get_file_by_known_name


def launch_game(ver: str, game_path: Path, profile: dict, token: str, loader: ModloaderEnum = ModloaderEnum.VANILLA, loader_ver: str = ''):
    manifest = get_for_version(ver)
    classpath = get_libs_str(ver)
    entry = 'net.minecraft.client.main.Main'
    cmd = [
        'java', f'-Djava.library.path={NATIVES / ver}',
    ]

    if loader == ModloaderEnum.FABRIC:
        classpath += os.pathsep + get_fabric_str(ver, loader_ver)
        entry = 'net.fabricmc.loader.impl.launch.knot.KnotClient'

        r = renamed(f'client-{ver}.jar')
        if not r.exists(): rename_file(get_file_by_known_name(f'client-{ver}.jar', ChecksumEnum.SHA1), f'client-{ver}.jar')

        classpath += os.pathsep + str(r)
    else:
        classpath += os.pathsep + str(get_file_by_known_name(f'client-{ver}.jar', ChecksumEnum.SHA1))

    cmd += [
        '-cp', classpath,
        entry,
        '--username', profile['name'],
        '--version', ver,
        '--gameDir', str(game_path),
        '--logFile', str(game_path / 'logs' / 'latest.log'),
        '--assetsDir', str(ASSETS),
        '--assetIndex', manifest['assetIndex']['id'],
        '--uuid', profile['id'],
        '--userType', 'msa',
    ]

    logger.debug(cmd)
    cmd += ['--accessToken', token]
    return subprocess.Popen(cmd, cwd=game_path)

if __name__ == "__main__":
    import asyncio
    msa = get_msa_token()
    prof, token = asyncio.run(do_full_auth(msa))
    launch_game('26.1.2', Path('/home/wojtmic/.local/share/lazurich/instances/60168p19/.minecraft/'), prof, token)
