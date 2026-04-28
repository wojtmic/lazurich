from dataclasses import dataclass
from enum import IntEnum, StrEnum
from pathlib import Path

class ChecksumEnum(StrEnum):
    SHA256 = 'sha256'
    SHA1   = 'sha1'
    SHA512 = 'sha512'
    MD5    = 'md5'

class ModloaderEnum(IntEnum):
    VANILLA = 0
    FABRIC = 1
    FORGE = 2
    QUILT = 3
    NEOFORGE = 4

@dataclass
class DownloadItem:
    checksum: str
    checksum_type: ChecksumEnum
    link: str

@dataclass
class Instance:
    name: str
    version: str
    modloader: ModloaderEnum
    modloader_version: str
