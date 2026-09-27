from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

class _Tolerant(StrEnum):
    @classmethod
    def _missing_(cls, value: object):
        return cls("unknown")

class Action(StrEnum):
    ALLOW = "allow"
    DISALLOW = "disallow"

class OsName(_Tolerant):
    WINDOWS = "windows"
    OSX = "osx"
    LINUX = "linux"
    UNKNOWN = "unknown"

class Arch(_Tolerant):
    X86 = "x86"
    X86_64 = "x86_64"
    ARM64 = "arm64"
    UNKNOWN = "unknown"

class VersionType(_Tolerant):
    RELEASE = "release"
    SNAPSHOT = "snapshot"
    OLD_BETA = "old_beta"
    OLD_ALPHA = "old_alpha"
    UNKNOWN = "unknown"

class LibraryRole(StrEnum):
    CLASSPATH = "classpath"
    NATIVE = "native"  # pre-1.19, extracted into the natives dir

@dataclass(frozen=True, slots=True)
class OsRule:
    name: OsName | None = None
    version: str | None = None  # regex
    arch: Arch | None = None

@dataclass(frozen=True, slots=True)
class Rule:
    action: Action
    os: OsRule | None = None
    features: tuple[tuple[str, bool], ...] = ()

@dataclass(frozen=True, slots=True)
class Download:
    url: str
    sha1: str
    size: int
    path: str | None = None

@dataclass(frozen=True, slots=True)
class Library:
    name: str
    role: LibraryRole
    download: Download | None = None
    rules: tuple[Rule, ...] = ()
    extract_exclude: tuple[str, ...] = ()

@dataclass(frozen=True, slots=True)
class Arg:
    value: tuple[str, ...]
    rules: tuple[Rule, ...] = ()

@dataclass(frozen=True, slots=True)
class AssetIndex:
    id: str
    download: Download
    total_size: int

@dataclass(frozen=True, slots=True)
class Logging:
    argument: str
    file: Download

@dataclass(frozen=True, slots=True)
class Profile:
    id: str
    type: VersionType
    release_time: datetime
    main_class: str
    java_major: int
    java_component: str | None
    client: Download | None
    asset_index: AssetIndex | None
    libraries: tuple[Library, ...]
    game_args: tuple[Arg, ...]
    jvm_args: tuple[Arg, ...]
    logging: Logging | None = None
    parent: str | None = None

@dataclass(frozen=True, slots=True)
class VersionEntry:
    id: str
    type: VersionType
    url: str
    sha1: str
    release_time: datetime

@dataclass(frozen=True, slots=True)
class VersionManifest:
    latest_release: str
    latest_snapshot: str
    versions: tuple[VersionEntry, ...] = ()