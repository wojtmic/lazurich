import subprocess
from pathlib import Path
import os
from loguru import logger

from lazurich.api.microsoft import do_full_auth, get_msa_token
from lazurich.api.mojang import get_for_version
from lazurich.core.models.general import ChecksumEnum
from lazurich.core.natives import get_libs_str
from lazurich.core.paths import NATIVES, ASSETS
from lazurich.core.store import get_file_by_known_name


def launch_game(ver: str, game_path: Path, profile: dict, token: str):
    manifest = get_for_version(ver)
    cmd = [
        'java', f'-Djava.library.path={NATIVES / ver}',
        '-cp', get_libs_str(ver) + os.pathsep + str(get_file_by_known_name(f'client-{ver}.jar', ChecksumEnum.SHA1)),
        'net.minecraft.client.main.Main',
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
    subprocess.run(cmd, cwd=game_path)

if __name__ == "__main__":
    import asyncio
    msa = get_msa_token()
    prof, token = asyncio.run(do_full_auth(msa))
    launch_game('26.1.2', Path('/home/wojtmic/.local/share/lazurich/instances/60168p19/.minecraft/'), prof, token)
