import hashlib
import json

from lazurich import get_client
from lazurich.api.mojang.data import Profile, VersionEntry, VersionManifest
from lazurich.api.mojang.normalize import normalize, normalize_manifest

MANIFEST_URL = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"

class ChecksumError(Exception):
    pass

async def fetch_manifest() -> VersionManifest:
    response = await get_client().get(MANIFEST_URL)
    response.raise_for_status()
    return normalize_manifest(response.json())

async def fetch_version(entry: VersionEntry) -> Profile:
    response = await get_client().get(entry.url)
    response.raise_for_status()

    data = response.content
    actual = hashlib.sha1(data).hexdigest()
    if actual != entry.sha1:
        raise ChecksumError(f"{entry.id}: expected sha1 {entry.sha1}, got {actual}")

    return normalize(json.loads(data))

async def fetch_version_by_id(version_id: str) -> Profile:
    manifest = await fetch_manifest()
    entry = next((v for v in manifest.versions if v.id == version_id), None)
    if entry is None:
        raise KeyError(f"unknown version: {version_id}")
    return await fetch_version(entry)