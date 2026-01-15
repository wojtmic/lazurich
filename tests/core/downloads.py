import pytest
import respx
import hashlib
from pathlib import Path
from httpx import Response, AsyncClient
from lazurich.core.models.general import ChecksumEnum, DownloadItem
from lazurich.core.network import download_file, download_batch

def sha256(content: bytes):
    return hashlib.sha256(content).hexdigest()
