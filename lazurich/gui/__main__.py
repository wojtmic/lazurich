from pathlib import Path
import slint
from lazurich.gui.theme import apply_theme
import os
import sys

ThemeDebugWindow = slint.load_file(Path(__file__).parent / "layouts" / "dev" / "theme_debug.slint").ThemeDebugWindow

THEME_DIR = Path(os.environ.get('LAZURICH_THEME', Path(__file__).parent / 'theme'))

class App(slint.load_file(Path(__file__).parent / 'layouts' / 'main.slint').AppWindow):
    @slint.callback
    async def b_launch_game(self):
        print('game')

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