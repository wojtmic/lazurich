import subprocess

from lazurich.api.mojang import get_for_version
from lazurich.core.models.general import ChecksumEnum
from lazurich.core.natives import get_libs_str
from lazurich.core.paths import NATIVES, ASSETS
from lazurich.core.store import get_file_by_known_name


def launch_game(ver: str):
    manifest = get_for_version(ver)
    subprocess.run([
        'java', f'-Djava.library.path={NATIVES / ver}',
        '-cp', get_libs_str(ver) + ':' + str(get_file_by_known_name(f'client-{ver}.jar', ChecksumEnum.SHA1)),
        'net.minecraft.client.main.Main',
        '--username', 'real',
        '--version', ver,
        '--gameDir', str('.minecraft'),
        '--assetsDir', str(ASSETS),
        '--assetIndex', manifest['assetIndex']['id'],
        '--uuid', '00-00-00000-00000-00000',
        '--accessToken', '0',
        '--userType', 'legacy',
    ])

if __name__ == "__main__":
    launch_game('26.1.2')
