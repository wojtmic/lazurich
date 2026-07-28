import gettext
from pathlib import Path

import polib
from loguru import logger

from lazurich.core.paths import LANG

DOMAIN = 'lazurich'
SOURCE_DIR = Path(__file__).parent.parent / 'gui' / 'lang'

def compile_translations() -> None:
    for po_path in SOURCE_DIR.glob(f'*/LC_MESSAGES/{DOMAIN}.po'):
        locale = po_path.parent.parent.name
        mo_dir = LANG / locale / 'LC_MESSAGES'
        mo_dir.mkdir(parents=True, exist_ok=True)
        mo_path = mo_dir / f'{DOMAIN}.mo'

        po = polib.pofile(str(po_path))
        po.save_as_mofile(str(mo_path))
        logger.debug(f'Compiled {po_path} -> {mo_path}')


def load_translations(locale: str) -> gettext.NullTranslations:
    try:
        return gettext.translation(DOMAIN, str(LANG), [locale])
    except FileNotFoundError:
        logger.debug(f'No compiled translation for locale {locale!r}')
        return gettext.NullTranslations()