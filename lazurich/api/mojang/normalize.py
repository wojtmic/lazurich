from datetime import datetime
from typing import Any

from lazurich.api.mojang.data import (
    Action,
    Arch,
    Arg,
    AssetIndex,
    Download,
    Library,
    LibraryRole,
    Logging,
    OsName,
    OsRule,
    Profile,
    Rule,
    VersionEntry,
    VersionManifest,
    VersionType,
)

# pre-1.13 JSONs have no JVM args, the launcher supplies these
LEGACY_JVM_ARGS = (
    Arg(("-Djava.library.path=${natives_directory}",)),
    Arg(("-Dminecraft.launcher.brand=${launcher_name}",)),
    Arg(("-Dminecraft.launcher.version=${launcher_version}",)),
    Arg(("-cp", "${classpath}")),
)

# ${arch} in old classifiers means JVM bitness
BITNESS = {"32": Arch.X86, "64": Arch.X86_64}

ALLOW_ALL = Rule(Action.ALLOW)

def normalize_manifest(raw: dict[str, Any]) -> VersionManifest:
    return VersionManifest(
        latest_release=raw["latest"]["release"],
        latest_snapshot=raw["latest"]["snapshot"],
        versions=tuple(
            VersionEntry(
                id=v["id"],
                type=VersionType(v["type"]),
                url=v["url"],
                sha1=v["sha1"],
                release_time=datetime.fromisoformat(v["releaseTime"]),
            )
            for v in raw["versions"]
        ),
    )

def normalize(raw: dict[str, Any]) -> Profile:
    if "arguments" in raw:
        game_args = parse_args(raw["arguments"].get("game", []))
        jvm_args = parse_args(raw["arguments"].get("jvm", []))
    else:
        game_args = parse_legacy_args(raw.get("minecraftArguments", ""))
        jvm_args = LEGACY_JVM_ARGS

    java = raw.get("javaVersion") or {}
    downloads = raw.get("downloads") or {}

    return Profile(
        id=raw["id"],
        type=VersionType(raw.get("type", "unknown")),
        release_time=datetime.fromisoformat(raw["releaseTime"]),
        main_class=raw["mainClass"],
        java_major=java.get("majorVersion", 8),
        java_component=java.get("component"),
        client=parse_download(downloads["client"]) if "client" in downloads else None,
        asset_index=parse_asset_index(raw["assetIndex"]) if "assetIndex" in raw else None,
        libraries=tuple(lib for entry in raw.get("libraries", []) for lib in parse_library(entry)),
        game_args=game_args,
        jvm_args=jvm_args,
        logging=parse_logging(raw.get("logging")),
        parent=raw.get("inheritsFrom"),
    )

def parse_download(raw: dict[str, Any], path: str | None = None) -> Download:
    return Download(url=raw["url"], sha1=raw["sha1"], size=raw["size"], path=raw.get("path", path))

def parse_asset_index(raw: dict[str, Any]) -> AssetIndex:
    return AssetIndex(id=raw["id"], download=parse_download(raw), total_size=raw["totalSize"])

def parse_logging(raw: dict[str, Any] | None) -> Logging | None:
    client = (raw or {}).get("client")
    if not client:
        return None
    file = client["file"]
    return Logging(argument=client["argument"], file=parse_download(file, path=file.get("id")))

def parse_rules(raw: list[dict[str, Any]] | None) -> tuple[Rule, ...]:
    rules = []
    for r in raw or ():
        os = r.get("os")
        os_rule = None
        if os:
            os_rule = OsRule(
                name=OsName(os["name"]) if "name" in os else None,
                version=os.get("version"),
                arch=Arch(os["arch"]) if "arch" in os else None,
            )
        features = tuple(sorted((r.get("features") or {}).items()))
        rules.append(Rule(Action(r["action"]), os_rule, features))
    return tuple(rules)

def parse_args(raw: list[str | dict[str, Any]]) -> tuple[Arg, ...]:
    args = []
    for item in raw:
        if isinstance(item, str):
            args.append(Arg((item,)))
            continue
        value = item["value"]
        tokens = (value,) if isinstance(value, str) else tuple(value)
        args.append(Arg(tokens, parse_rules(item.get("rules"))))
    return tuple(args)

def parse_legacy_args(raw: str) -> tuple[Arg, ...]:
    return tuple(Arg((token,)) for token in raw.split())

def parse_library(raw: dict[str, Any]) -> list[Library]:
    name = raw["name"]
    rules = parse_rules(raw.get("rules"))
    downloads = raw.get("downloads") or {}
    out = []

    # natives-only entries have no artifact
    if "artifact" in downloads or "natives" not in raw:
        artifact = downloads.get("artifact")
        out.append(Library(
            name=name,
            role=LibraryRole.CLASSPATH,
            download=parse_download(artifact) if artifact else None,
            rules=rules,
        ))

    classifiers = downloads.get("classifiers") or {}
    exclude = tuple((raw.get("extract") or {}).get("exclude", ()))
    for os_name, template in (raw.get("natives") or {}).items():
        os = OsName(os_name)
        if "${arch}" in template:
            variants = [(template.replace("${arch}", bits), arch) for bits, arch in BITNESS.items()]
        else:
            variants = [(template, None)]

        for classifier, arch in variants:
            dl = classifiers.get(classifier)
            if dl is None:  # declared but never published, e.g. twitch natives-linux
                continue
            out.append(Library(
                name=f"{name}:{classifier}",
                role=LibraryRole.NATIVE,
                download=parse_download(dl),
                rules=restrict(rules, os, arch),
                extract_exclude=exclude,
            ))
    return out

# last match wins, so appending disallows for every other os/arch ANDs them onto upstream rules
def restrict(rules: tuple[Rule, ...], os: OsName, arch: Arch | None) -> tuple[Rule, ...]:
    extra = [Rule(Action.DISALLOW, OsRule(name=o)) for o in OsName if o not in (os, OsName.UNKNOWN)]
    if arch is not None:
        extra += [Rule(Action.DISALLOW, OsRule(arch=a)) for a in Arch if a not in (arch, Arch.UNKNOWN)]
    return (rules or (ALLOW_ALL,)) + tuple(extra)