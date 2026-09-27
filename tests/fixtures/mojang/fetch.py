import hashlib
import json
import urllib.request
from pathlib import Path

MANIFEST_URL = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
OUT = Path(__file__).parent

VERSIONS = ["1.7.10", "1.12.2", "1.13", "1.16.5", "1.18.2", "1.19"] # auto adds latest release and snapshot

def fetch(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read()

def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    raw = fetch(MANIFEST_URL)
    (OUT / "version_manifest_v2.json").write_bytes(raw)
    manifest = json.loads(raw)

    wanted = VERSIONS + [manifest["latest"]["release"], manifest["latest"]["snapshot"]]
    entries = {v["id"]: v for v in manifest["versions"]}

    for vid in wanted:
        entry = entries[vid]
        data = fetch(entry["url"])
        if hashlib.sha1(data).hexdigest() != entry["sha1"]:
            raise SystemExit(f"sha1 mismatch for {vid}")
        (OUT / f"{vid}.json").write_bytes(data)
        print(f"{vid}: ok")

if __name__ == "__main__":
    main()