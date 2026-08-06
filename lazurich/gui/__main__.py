import asyncio
from pathlib import Path
import slint
import os
import sys
import subprocess
import socket
import ctypes
from ctypes import wintypes

from loguru import logger

from lazurich.api.microsoft import get_msa_token, get_xbox_live_token, get_xsts_token, get_minecraft_token, get_minecraft_profile
from lazurich.core.instances import read_manifest
from lazurich.core.launcher import launch_game
from lazurich.core.paths import INSTANCES, SOCKET
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
    async def preview_error(self):
        self.error_active = True
        self.error_text = "my bad"

    async def display_error(self, err_text: str):
        self.error_active = True
        self.error_text = err_text


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

        logger.info(f'Launching instance {instance_id}')
        launch_game(instance.version, INSTANCES / instance_id / '.minecraft', profile, mc_token, instance.modloader, instance.modloader_version)

        self.progress_value = 1
        stages[5] = {"text": "Launching game", "done": True, "active": False}
        await asyncio.sleep(2)
        self.progress_active = False

    @slint.callback
    async def edit_instance(self, instance_id: str):
        print('edit instance trigger')
        manifest = await read_manifest()
        instance = manifest[instance_id]

        # self.instance_edit_id = instance_id
        self.instance_edit_name = instance.name
        self.instance_edit_visible = True

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


async def load_app(app, theme_success=0):
    if theme_success != 0:
        await app.display_error('Your theme has a version lower than the current standard! To avoid issues, the default theme has been loaded. Contact your theme\'s author and if you are, update it according to the docs!')

    manifest = await read_manifest()
    model = slint.ListModel([
        {"id": k, "name": v.name, "version": v.version}
        for k, v in manifest.items()
    ])
    app._instance_list_model = model
    app.instance_list = model

def show_already_running_error():
    dialog = slint.load_file(Path(__file__).parent / "layouts" / "popups" / "already_running.slint").ErrorDialog()
    dialog.show()
    dialog.run()
    sys.exit(0)

def main():
    if get_os_name() != "windows":
        if SOCKET.exists():
            probe = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            try:
                probe.connect(str(SOCKET))
                probe.close()
                show_already_running_error()
                return
            except (ConnectionRefusedError, FileNotFoundError):
                probe.close()
                SOCKET.unlink()

        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.bind(str(SOCKET))
        sock.listen(1)
    else:
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.CreateMutexW.restype = wintypes.HANDLE
        kernel32.CreateMutexW.argtypes = [wintypes.LPCVOID, wintypes.BOOL, wintypes.LPCWSTR]

        mutex = kernel32.CreateMutexW(None, False, "Global\\Lazurich")
        if ctypes.get_last_error() == 183:
            show_already_running_error()
            return

    app = App()
    theme_success = apply_theme(app, Path(__file__).parent / "theme")
    app.dev = os.environ.get('LAZURICH_DEV', 'false').lower() == 'true' or '--dev' in sys.argv
    app.git_hash = get_git_hash()
    # app.run()

    app.show()
    slint.run_event_loop(load_app(app, theme_success))
    app.hide()

    if get_os_name() != 'windows':
        sock.close()
        os.unlink(SOCKET)
    else:
        kernel32.CloseHandle(mutex)

if __name__ == "__main__":
    main()
