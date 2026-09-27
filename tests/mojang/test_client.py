import hashlib
from datetime import datetime

import httpx
import pytest
from conftest import FIXTURES

from lazurich.api.mojang import VersionEntry, VersionType
from lazurich.api.mojang import client as mojang_client
from lazurich.api.mojang.client import (
    MANIFEST_URL,
    ChecksumError,
    fetch_manifest,
    fetch_version,
    fetch_version_by_id,
)

VERSION_URL = "https://piston-meta.mojang.com/v1/packages/test/1.7.10.json"
VERSION_BYTES = (FIXTURES / "1.7.10.json").read_bytes()

def handler(request: httpx.Request) -> httpx.Response:
    if str(request.url) == MANIFEST_URL:
        return httpx.Response(200, content=(FIXTURES / "version_manifest_v2.json").read_bytes())
    if str(request.url) == VERSION_URL:
        return httpx.Response(200, content=VERSION_BYTES)
    return httpx.Response(404)

@pytest.fixture
def anyio_backend():
    return "asyncio"

@pytest.fixture(autouse=True)
def mock_http(monkeypatch):
    fake = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    monkeypatch.setattr(mojang_client, "get_client", lambda: fake)

def entry(url: str = VERSION_URL, sha1: str | None = None) -> VersionEntry:
    return VersionEntry(
        id="1.7.10",
        type=VersionType.RELEASE,
        url=url,
        sha1=sha1 or hashlib.sha1(VERSION_BYTES).hexdigest(),
        release_time=datetime.now(),
    )

@pytest.mark.anyio
async def test_fetch_manifest():
    manifest = await fetch_manifest()
    assert manifest.latest_release in {v.id for v in manifest.versions}

@pytest.mark.anyio
async def test_fetch_version():
    profile = await fetch_version(entry())
    assert profile.id == "1.7.10"

@pytest.mark.anyio
async def test_checksum_mismatch():
    with pytest.raises(ChecksumError):
        await fetch_version(entry(sha1="0" * 40))

@pytest.mark.anyio
async def test_http_error():
    with pytest.raises(httpx.HTTPStatusError):
        await fetch_version(entry(url="https://piston-meta.mojang.com/missing.json"))

@pytest.mark.anyio
async def test_unknown_version_id():
    with pytest.raises(KeyError):
        await fetch_version_by_id("not-a-version")