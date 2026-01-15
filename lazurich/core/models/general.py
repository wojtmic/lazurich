from dataclasses import dataclass
from enum import IntEnum, StrEnum

class ChecksumEnum(StrEnum):
    SHA256 = 'sha256'
    SHA1   = 'sha1'
    SHA512 = 'sha512'
    MD5    = 'md5'

@dataclass
class DownloadItem:
    checksum: str
    checksum_type: ChecksumEnum
    link: str
