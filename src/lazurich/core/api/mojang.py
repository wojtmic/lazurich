import json
import platform
from datetime import datetime
from itertools import count

from loguru import logger

from lazurich.core.cache.db import db
from lazurich.core.cache.mojang import AssetIndex, Library, Version, VersionLibrary
from lazurich.core.network import client

c = client()

PISTON_BASE = 'https://piston-meta.mojang.com/'

async def manifests():
    logger.debug('Fetching version manifest')
    resp = await c.get(PISTON_BASE + 'mc/game/version_manifest_v2.json')
    data = json.loads(resp.content)
    versions = data['versions']

    with db.atomic():
        for v in versions:
            Version.insert(
                id=v['id'],
                type=v['type'],
                release_time=datetime.fromisoformat(v['releaseTime']),
                time=datetime.fromisoformat(v['time']),
                meta_sha1=v['sha1'],
                compliance_level=v['complianceLevel'],
            ).on_conflict(
                conflict_target=[Version.id],
                preserve=[
                    Version.type,
                    Version.release_time,
                    Version.time,
                    Version.meta_sha1,
                    Version.compliance_level,
                ],
            ).execute()
            logger.debug(v)

def cache_ver(data: dict):
    ai = data['assetIndex']
    _, created = AssetIndex.get_or_create(
        id=ai['id'],
        defaults=dict(url=ai['url'], sha1=ai['sha1'], size=ai['size'], total_size=ai['totalSize']),
    )
    logger.debug(f'Asset index {ai["id"]} ({"new" if created else "cached"})')

    java = data.get('javaVersion', {'component': 'jre-legacy', 'majorVersion': 8})
    Version.update(
        main_class=data['mainClass'],
        java_component=java['component'],
        java_major=java['majorVersion'],
        asset_index=ai['id'],
    ).where(Version.id == data['id']).execute()
    logger.debug(
        f'Version {data["id"]}: main={data["mainClass"]}, '
        f'java={java["component"]} ({java["majorVersion"]})'
    )

OS_NAME = {'Linux': 'linux', 'Darwin': 'osx', 'Windows': 'windows'}[platform.system()]
IS_X86 = platform.machine().lower() in ('i386', 'i686', 'x86')
ARCH = {'x86_64': 'x86_64', 'amd64': 'x86_64', 'aarch64': 'aarch_64', 'arm64': 'aarch_64',
        'i386': 'x86', 'i686': 'x86'}.get(platform.machine().lower())

def _rule_matches(rule: dict) -> bool:
    if 'features' in rule:
        return False
    os = rule.get('os', {})
    if 'name' in os and os['name'] != OS_NAME:
        return False
    return not ('arch' in os and os['arch'] != ARCH)

def _allowed(rules: list[dict] | None) -> bool:
    if not rules:
        return True
    allowed = False
    for rule in rules:
        if _rule_matches(rule):
            allowed = rule['action'] == 'allow'
    return allowed

def _link(vid, pos, name, info, kind, exclude=None):
    lib, created = Library.get_or_create(
        name=name,
        defaults=dict(
            kind=kind,
            path=info['path'],
            url=info['url'],
            sha1=info['sha1'],
            size=info['size'],
            extract_exclude=exclude,
        ),
    )
    VersionLibrary.create(version=vid, library=lib, position=pos)
    logger.debug(f'  [{pos}] {kind} {name}{" (new)" if created else ""}')

def cache_libs(data: dict):
    vid, pos = data['id'], count()
    VersionLibrary.delete().where(VersionLibrary.version == vid).execute()
    logger.debug(f'Linking {len(data["libraries"])} library entries for {vid}')
    for lib in data['libraries']:
        if not _allowed(lib.get('rules')):
            logger.debug(f'  skipped {lib["name"]} (rules)')
            continue
        dl = lib['downloads']
        if cls := lib.get('natives', {}).get(OS_NAME):
            cls = cls.replace('${arch}', '32' if IS_X86 else '64')
            if info := dl.get('classifiers', {}).get(cls):
                _link(vid, next(pos), f'{lib["name"]}:{cls}', info, 'native',
                      lib.get('extract', {}).get('exclude'))
            else:
                logger.debug(f'  missing classifier {cls} for {lib["name"]}')
        if 'artifact' in dl:
            _link(vid, next(pos), lib['name'], dl['artifact'], 'library')

    if cl := data.get('downloads', {}).get('client'):
        path = f'com/mojang/minecraft/{vid}/minecraft-{vid}-client.jar'
        _link(vid, next(pos), f'com.mojang:minecraft:{vid}:client', {**cl, 'path': path}, 'client')

async def get_for_version(ver: str, hash: str):
    logger.debug(f'Fetching version JSON for {ver} ({hash})')
    resp = await c.get(PISTON_BASE + 'v1/packages/' + hash + '/' + ver + '.json')
    data = json.loads(resp.content)

    with db.atomic():
        cache_ver(data)
        cache_libs(data)
        Version.update(detail_sha1=hash).where(Version.id == ver).execute()
    logger.debug(f'Cached {ver}')

if __name__ == '__main__':
    from lazurich.core.cache.db import init_db

    init_db()
    import asyncio

    # asyncio.run(manifests())
    v = Version.get_by_id("26.1.2")
    asyncio.run(get_for_version(v.id, v.meta_sha1))
