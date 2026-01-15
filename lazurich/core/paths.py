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
    INSTANCES.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    STORE.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    NATIVES.mkdir(parents=True, exist_ok=True)
    JARS.mkdir(parents=True, exist_ok=True)
    TEMPLATES.mkdir(parents=True, exist_ok=True)
    EXTENSIONS.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)

    SHA256.mkdir(parents=True, exist_ok=True)
    SHA512.mkdir(parents=True, exist_ok=True)
    SHA1.mkdir(parents=True, exist_ok=True)
    MD5.mkdir(parents=True, exist_ok=True)
