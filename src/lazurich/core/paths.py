from pathlib import Path
import platform
import os

plat = platform.system()

if plat.lower() != 'windows':
    USER_ROOT = Path.home()
    l = USER_ROOT / '.local'
    DATA_ROOT = l / 'share' / 'lazurich'
    CACHE_FILE = l / '.cache' / 'lazurich_cache.db'
else:
    USER_ROOT = Path.home()
    l = USER_ROOT / 'AppData'
    DATA_ROOT = l / 'Roaming' / 'lazurich'
    CACHE_FILE = DATA_ROOT / 'cache.db'

if os.environ.get('LAZURICH_CACHE_FILE'): CACHE_FILE = Path(os.environ.get('LAZURICH_CACHE_FILE')).expanduser()
