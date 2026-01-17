from pathlib import Path
import os

xdg_storage  = os.environ.get('XDG_DATA_HOME', '~/.local/share')
xdg_state    = os.environ.get('XDG_STATE_HOME', '~/.local/state')
xdg_config   = os.environ.get('XDG_CONFIG_HOME', '~/.config')

STORAGE_ROOT = Path(xdg_storage).expanduser() / 'lazurich'
LOG_ROOT     = Path(xdg_state)  .expanduser() / 'lazurich'
CONFIG_ROOT  = Path(xdg_config) .expanduser() / 'lazurich'
SOCKET       = Path(f'/run/user/{os.getuid()}/lazurich.sock')

# Storage subdirs
INSTANCES = STORAGE_ROOT / 'instances'
DATA      = STORAGE_ROOT / 'data'
STORE     = STORAGE_ROOT / 'store'
ASSETS    = STORAGE_ROOT / 'assets'
JARS      = STORAGE_ROOT / 'jars'
TEMPLATES = STORAGE_ROOT / 'templates'
EXTENSIONS= STORAGE_ROOT / 'extensions'

# Data files
CONFIG    = CONFIG_ROOT / 'config.json'
ACCOUNTS  = CONFIG_ROOT / 'accounts.json'
INSTANCE  = CONFIG_ROOT / 'instances.json'
TOKENS    = DATA / 'msal_token_cache-DO-NOT-SEND-TO-ANYONE.bin'

# Store structure
SHA256    = STORE / 'sha256'
SHA512    = STORE / 'sha512'
SHA1      = STORE / 'sha1'
MD5       = STORE / 'md5'

def create_paths():
    all_dirs = [INSTANCES, DATA, STORE, ASSETS, NATIVES, JARS,
                TEMPLATES, EXTENSIONS, SHA256, SHA512, SHA1, MD5, CONFIG_ROOT, LOG_ROOT]
    for directory in all_dirs:
        directory.mkdir(parents=True, exist_ok=True)
