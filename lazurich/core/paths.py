from pathlib import Path
import os

STORAGE_ROOT = Path('~/.local/share/lazurich').expanduser()
SOCKET       = Path(f'/run/user/{os.getuid()}/lazurich.sock')

# Storage subdirs
INSTANCES = STORAGE_ROOT / 'instances'
DATA      = STORAGE_ROOT / 'data'
STORE     = STORAGE_ROOT / 'store'
ASSETS    = STORAGE_ROOT / 'assets'
NATIVES   = STORAGE_ROOT / 'natives'
JARS      = STORAGE_ROOT / 'jars'
TEMPLATES = STORAGE_ROOT / 'templates'
EXTENSIONS= STORAGE_ROOT / 'extensions'
LOGS      = STORAGE_ROOT / 'logs'

# Data files
CONFIG    = DATA / 'config.json'
ACCOUNTS  = DATA / 'accounts.json'
TOKENS    = DATA / 'msal_token_cache-DO-NOT-SEND-TO-ANYONE.bin'

# Store structure
SHA256    = STORE / 'sha256'
SHA512    = STORE / 'sha512'
SHA1      = STORE / 'sha1'
MD5       = STORE / 'md5'

def create_paths():
    all_dirs = [INSTANCES, DATA, STORE, ASSETS, NATIVES, JARS,
                TEMPLATES, EXTENSIONS, LOGS, SHA256, SHA512, SHA1, MD5]
    for directory in all_dirs:
        directory.mkdir(parents=True, exist_ok=True)
