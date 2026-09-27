import subprocess
from pathlib import Path
import os
from loguru import logger

from lazurich.api.microsoft import do_full_auth, get_msa_token
from lazurich.api.mojang import get_for_version
from lazurich.core.models.general import ChecksumEnum, ModloaderEnum
from lazurich.core.modloaders.fabric import get_fabric_str
from lazurich.core.modloaders import neoforge
from lazurich.core.natives import get_libs_str
from lazurich.core.paths import NATIVES, ASSETS
from lazurich.core.renamer import renamed, rename_file
from lazurich.core.store import get_file_by_known_name


def dedupe_classpath(classpath: str) -> str:
    """Drop repeated entries, keeping first occurrence. The store is content-addressed,
    so a library shipped by both vanilla and a modloader resolves to the same path -
    and some loaders (BootstrapLauncher) reject a classpath containing it twice."""
    seen = set()
    parts = []
    for part in classpath.split(os.pathsep):
        if not part or part in seen:
            continue
        seen.add(part)
        parts.append(part)
    return os.pathsep.join(parts)


def launch_game(ver: str, game_path: Path, profile: dict, token: str, loader: ModloaderEnum = ModloaderEnum.VANILLA, loader_ver: str = ''):
    manifest = get_for_version(ver)
    classpath = get_libs_str(ver)
    entry = 'net.minecraft.client.main.Main'
    jvm_args = [f'-Djava.library.path={NATIVES / ver}']
    extra_game_args = []

    if loader == ModloaderEnum.FABRIC:
        classpath += os.pathsep + get_fabric_str(ver, loader_ver)
        entry = 'net.fabricmc.loader.impl.launch.knot.KnotClient'

        r = renamed(f'client-{ver}.jar')
        if not r.exists(): rename_file(get_file_by_known_name(f'client-{ver}.jar', ChecksumEnum.SHA1), f'client-{ver}.jar')

        classpath += os.pathsep + str(r)
    elif loader == ModloaderEnum.NEOFORGE:
        version_json = neoforge.get_version_json(loader_ver)

        # NeoForge's JVM args reference jars by ${library_directory}/<maven path>, and
        # Java derives module names from jar filenames - so its libraries need a
        # Maven-layout tree rather than the store's content-addressed hash paths.
        library_dir = neoforge.build_library_farm(version_json, loader_ver)

        classpath += os.pathsep + neoforge.get_neoforge_str(version_json, loader_ver)
        entry = version_json['mainClass']

        jvm_args += neoforge.get_neoforge_jvm_args(version_json, library_dir)
        extra_game_args = neoforge.get_neoforge_game_args(version_json)
    else:
        classpath += os.pathsep + str(get_file_by_known_name(f'client-{ver}.jar', ChecksumEnum.SHA1))

    classpath = dedupe_classpath(classpath)

    cmd = ['java'] + jvm_args + [
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
    ] + extra_game_args

    logger.debug(cmd)
    cmd += ['--accessToken', token]
    return subprocess.Popen(cmd, cwd=game_path)

if __name__ == "__main__":
    import asyncio
    msa = get_msa_token()
    prof, token = asyncio.run(do_full_auth(msa))
    launch_game('26.1.2', Path('/home/wojtmic/.local/share/lazurich/instances/60168p19/.minecraft/'), prof, token)