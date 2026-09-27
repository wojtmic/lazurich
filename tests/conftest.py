import json
from pathlib import Path

import pytest

from lazurich.api.mojang import Profile, normalize

FIXTURES = Path(__file__).parent / "fixtures" / "mojang"
VERSION_FILES = sorted(p for p in FIXTURES.glob("*.json") if p.name != "version_manifest_v2.json")

def load_raw(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())

@pytest.fixture
def load_version():
    def load(version_id: str) -> Profile:
        return normalize(load_raw(f"{version_id}.json"))

    return load