from functools import lru_cache

from lazurich.api import fabric
from lazurich.core.models.general import DownloadItem, ChecksumEnum

@lru_cache(maxsize=None)
def maven_path(name: str) -> str:
    group, artifact, version = name.split(':')
    return f"{group.replace('.', '/')}/{artifact}/{version}/{artifact}-{version}.jar"

@lru_cache(maxsize=None)
def make_fabric_downloads(mc_ver: str, loader_ver: str) -> list[DownloadItem]:
    meta = fabric.get_loader_meta(mc_ver, loader_ver)
    libs = meta['launcherMeta']['libraries']
    all_libs = libs.get('common', []) + libs.get('client', [])
    return [
        DownloadItem(lib['sha1'], ChecksumEnum.SHA1, lib['url'].rstrip('/') + '/' + maven_path(lib['name']))
        for lib in all_libs
    ]