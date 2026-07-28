import subprocess
from pathlib import Path
import slint
import os
import sys

from lazurich.core.utils import get_os_name
from lazurich.gui.theme import apply_theme
from lazurich.gui.i18n import compile_translations, load_translations

compile_translations()
translations = load_translations(os.environ.get('LAZURICH_LOCALE', 'en_US'))
slint.init_translations(translations)

ThemeDebugWindow = slint.load_file(Path(__file__).parent / "layouts" / "dev" / "theme_debug.slint").ThemeDebugWindow

THEME_DIR = Path(os.environ.get('LAZURICH_THEME', Path(__file__).parent / 'theme'))

class App(slint.load_file(Path(__file__).parent / 'layouts' / 'main.slint').AppWindow):
    @slint.callback
    async def open_folder(self):
        if get_os_name() == 'windows':
            subprocess.Popen(['explorer', Path(__file__).parent])
        else:
            subprocess.Popen(['xdg-open', Path(__file__).parent])

    _debug_window = None

    def reload_theme(self):
        apply_theme(self, THEME_DIR)
        if self._debug_window is not None:
            apply_theme(self._debug_window, THEME_DIR)

    @slint.callback
    async def open_theme_debug(self):
        if self._debug_window is None:
            self._debug_window = ThemeDebugWindow()
            self._debug_window.reload_theme = self.reload_theme
            apply_theme(self._debug_window, Path(__file__).parent / "theme")
        self._debug_window.show()

def main():
    app = App()
    apply_theme(app, Path(__file__).parent / "theme")
    app.dev = os.environ.get('LAZURICH_DEV', 'false').lower() == 'true' or '--dev' in sys.argv
    app.run()