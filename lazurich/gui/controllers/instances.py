import asyncio
import traceback

from PySide6.QtCore import QObject, Slot, Signal

from lazurich.api.microsoft import do_full_auth, get_msa_token
from lazurich.core.instances import read_manifest
from lazurich.core.launcher import launch_game
from lazurich.core.paths import INSTANCES
from lazurich.gui.models.instances import InstanceListModel


class InstanceController(QObject):
    errorOccurred = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = InstanceListModel(self)

    @Slot()
    def refresh(self):
        asyncio.ensure_future(self._refresh())

    async def _refresh(self):
        try:
            instances = await read_manifest()
            self.model.set_instances(instances)
        except Exception:
            self.errorOccurred.emit(traceback.format_exc())

    @Slot(str, str)
    def launch(self, instance_id: str, version: str):
        asyncio.ensure_future(self._launch(instance_id, version))

    async def _launch(self, instance_id: str, version: str):
        try:
            # print(f"launching {instance_id}, {version}")
            msa = get_msa_token()
            prof, token = await do_full_auth(msa)
            launch_game(version, INSTANCES / instance_id, prof, token)
        except Exception:
            self.errorOccurred.emit(traceback.format_exc())