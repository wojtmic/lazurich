import tempfile
from pathlib import Path
import os

from lazurich.core.utils import get_os_name

if get_os_name() != 'windows':
    storage  = os.environ.get('XDG_DATA_HOME', '~/.local/share')
    state    = os.environ.get('XDG_STATE_HOME', '~/.local/state')
    config   = os.environ.get('XDG_CONFIG_HOME', '~/.config')
else:
    usr_root = os.path.expandvars(r'C:\Users\%USERNAME%\AppData')
    storage  = os.environ.get('LOCALAPPDATA', f'{usr_root}\\Local')
    state    = os.environ.get('LOCALAPPDATA', f'{usr_root}\\Local')
    config   = os.environ.get('APPDATA', f'{usr_root}\\Roaming')

STORAGE_ROOT = Path(storage).expanduser() / 'lazurich'
STATE_ROOT   = Path(state)  .expanduser() / 'lazurich'
CONFIG_ROOT  = Path(config) .expanduser() / 'lazurich'

WORKING      = Path(tempfile.gettempdir()) / 'lazurich'

if get_os_name() != 'windows':
    # DEV NOTE #1
    # Socket can also be a lockfile, on Windows. If it's a lockfile, USING_SOCKET will be False
    SOCKET       = Path(f'/run/user/{os.getuid()}/lazurich.sock')
    USING_SOCKET = True
else:
    SOCKET       = STATE_ROOT / 'lockfile'
    USING_SOCKET = False

# Storage subdirs
INSTANCES  = STORAGE_ROOT / 'instances'
STORE      = STORAGE_ROOT / 'store'
ASSETS     = STORAGE_ROOT / 'assets'
TEMPLATES  = STORAGE_ROOT / 'templates'
EXTENSIONS = STORAGE_ROOT / 'extensions'
NATIVES    = STORAGE_ROOT / 'natives'

LOGS       = STATE_ROOT / 'logs'

# Data files
CONFIG     = CONFIG_ROOT / 'config.json'
ACCOUNTS   = CONFIG_ROOT / 'accounts.json'
INSTANCE   = CONFIG_ROOT / 'instances.toml'

# Store structure
SHA256     = STORE / 'sha256'
SHA512     = STORE / 'sha512'
SHA1       = STORE / 'sha1'
MD5        = STORE / 'md5'

def create_paths():
    all_dirs = [INSTANCES, STORE, ASSETS, WORKING, LOGS,
                TEMPLATES, EXTENSIONS, SHA256, SHA512, SHA1, MD5, CONFIG_ROOT, STATE_ROOT]
    for directory in all_dirs:
        directory.mkdir(parents=True, exist_ok=True)
