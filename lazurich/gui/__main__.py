import sys
from pathlib import Path

import qasync
from PySide6.QtGui import QGuiApplication, QIcon, QPixmap

from lazurich.api.microsoft import get_msa_token, do_full_auth
from lazurich.core.launcher import launch_game
from lazurich.core.paths import INSTANCES

from lazurich.gui.events import on_button_press
from lazurich.gui.loader import init_qml, load_qml


@on_button_press('launchButton')
async def launch_game_button():
    msa = get_msa_token()
    prof, token = await do_full_auth(msa)
    launch_game('26.1.2', INSTANCES / '60168p19' / '.minecraft', prof, token)

if __name__ == "__main__":
    app = QGuiApplication(sys.argv)

    pixmap = QPixmap(str(Path(__file__).resolve().parent / 'logo.png'))
    icon = QIcon()
    icon.addPixmap(pixmap)
    app.setWindowIcon(icon)

    loop = qasync.QEventLoop(app)
    qasync.asyncio.set_event_loop(loop)

    init_qml()

    load_qml('contentSlot', 'LaunchButton.qml')

    with loop:
        sys.exit(loop.run_forever())