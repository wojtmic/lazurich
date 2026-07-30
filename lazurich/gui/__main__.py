import asyncio
from pathlib import Path
import slint
import os
import sys
import subprocess

from lazurich.api.microsoft import do_full_auth, get_msa_token, get_xbox_live_token, get_xsts_token, \
    get_minecraft_token, get_minecraft_profile
from lazurich.core.instances import read_manifest
from lazurich.core.launcher import launch_game
from lazurich.core.paths import INSTANCES
from lazurich.core.utils import get_os_name
from lazurich.gui.theme import apply_theme
from lazurich.gui.i18n import compile_translations, load_translations

def get_git_hash() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=Path(__file__).parent,
            text=True,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"

compile_translations()
translations = load_translations(os.environ.get('LAZURICH_LOCALE', 'en_US'))
slint.init_translations(translations)

ThemeDebugWindow = slint.load_file(Path(__file__).parent / "layouts" / "dev" / "theme_debug.slint").ThemeDebugWindow

THEME_DIR = Path(os.environ.get('LAZURICH_THEME', Path(__file__).parent / 'theme'))

class App(slint.load_file(Path(__file__).parent / 'layouts' / 'main.slint').AppWindow):
    @slint.callback
    async def preview_progress(self):
        self.progress_active = True
        self.progress_stage = "Thingamabobbing"
        self.progress_value = 0
        self._progress_stages_model = slint.ListModel([
            {"text": "Thingamabobbing", "done": False, "active": True},
            {"text": "Procrastinating", "done": False, "active": False},
            {"text": "Goofing and Gaffing", "done": False, "active": False},
            {"text": "Doohickeying", "done": False, "active": False},
        ])
        self.progress_stages = self._progress_stages_model
        stages = self._progress_stages_model
        await asyncio.sleep(2)

        stages[0] = {"text": "Thingamabobbing", "done": True, "active": False}
        stages[1] = {"text": "Procrastinating", "done": False, "active": True}
        self.progress_stage = "Procrastinating"
        self.progress_value = 0.25
        await asyncio.sleep(3)

        stages[1] = {"text": "Procrastinating", "done": True, "active": False}
        stages[2] = {"text": "Goofing and Gaffing", "done": False, "active": True}
        self.progress_stage = "Goofing and Gaffing"
        self.progress_value = 0.5
        await asyncio.sleep(1)

        stages[2] = {"text": "Goofing and Gaffing", "done": True, "active": False}
        stages[3] = {"text": "Doohickeying", "done": False, "active": True}
        self.progress_stage = "Doohickeying"
        self.progress_value = 0.75
        await asyncio.sleep(1)

        self.progress_value = 1
        stages[3] = {"text": "Doohickeying", "done": True, "active": False}
        await asyncio.sleep(2)


        self.progress_active = False

    @slint.callback
    async def launch_instance(self, instance_id: str):
        self.progress_active = True
        self.progress_value = 0
        self.progress_stage = "Getting MSA Token"
        self._progress_stages_model = slint.ListModel([
            {"text": "MSA Token", "done": False, "active": True},
            {"text": "XBOX Live Token", "done": False, "active": False},
            {"text": "XSTS Token", "done": False, "active": False},
            {"text": "Minecraft Token", "done": False, "active": False},
            {"text": "Fetching profile", "done": False, "active": False},
            {"text": "Launching game", "done": False, "active": False},
        ])
        self.progress_stages = self._progress_stages_model
        stages = self._progress_stages_model
        msa = get_msa_token()

        self.progress_stage = "Getting Xbox Live Token"
        stages[0] = {"text": "MSA Token", "done": True, "active": False}
        stages[1] = {"text": "XBOX Live Token", "done": False, "active": True}
        xbl_token, uhs = await get_xbox_live_token(msa)

        self.progress_value = 0.2
        self.progress_stage = "Getting XSTS Live Token"
        stages[1] = {"text": "XBOX Live Token", "done": True, "active": False}
        stages[2] = {"text": "XSTS Token", "done": False, "active": True}
        xsts_token = await get_xsts_token(xbl_token)

        self.progress_value = 0.4
        self.progress_stage = "Getting Minecraft Token"
        stages[2] = {"text": "XSTS Token", "done": True, "active": False}
        stages[3] = {"text": "Minecraft Token", "done": False, "active": True}
        mc_token = await get_minecraft_token(uhs, xsts_token)

        self.progress_value = 0.6
        self.progress_stage = "Fetching Minecraft profile"
        stages[3] = {"text": "Minecraft Token", "done": True, "active": False}
        stages[4] = {"text": "Fetching profile", "done": False, "active": True}
        profile = await get_minecraft_profile(mc_token)

        self.progress_value = 0.8
        self.progress_stage = "Launching game"
        stages[4] = {"text": "Fetching profile", "done": True, "active": False}
        stages[5] = {"text": "Launching game", "done": False, "active": True}

        manifest = await read_manifest()
        instance = manifest[instance_id]

        launch_game(instance.version, INSTANCES / instance_id / '.minecraft', profile, mc_token)

        self.progress_value = 1
        stages[5] = {"text": "Launching game", "done": True, "active": False}
        await asyncio.sleep(2)
        self.progress_active = False

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


async def load_instances(app):
    manifest = await read_manifest()
    model = slint.ListModel([
        {"id": k, "name": v.name, "version": v.version}
        for k, v in manifest.items()
    ])
    app._instance_list_model = model
    app.instance_list = model

def main():
    app = App()
    apply_theme(app, Path(__file__).parent / "theme")
    app.dev = os.environ.get('LAZURICH_DEV', 'false').lower() == 'true' or '--dev' in sys.argv
    app.git_hash = get_git_hash()
    # app.run()

    app.show()
    slint.run_event_loop(load_instances(app))
    app.hide()
