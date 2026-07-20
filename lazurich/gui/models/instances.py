from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt, Signal

from lazurich.core.models.general import Instance, ModloaderEnum

MODLOADER_NAMES = {
    ModloaderEnum.VANILLA: "Vanilla",
    ModloaderEnum.FABRIC: "Fabric",
    ModloaderEnum.FORGE: "Forge",
    ModloaderEnum.QUILT: "Quilt",
    ModloaderEnum.NEOFORGE: "NeoForge",
}


class InstanceListModel(QAbstractListModel):
    IdRole = Qt.UserRole + 1
    NameRole = Qt.UserRole + 2
    VersionRole = Qt.UserRole + 3
    ModloaderRole = Qt.UserRole + 4
    ModloaderVersionRole = Qt.UserRole + 5
    LastPlayedRole = Qt.UserRole + 6
    PlaytimeRole = Qt.UserRole + 7
    IconRole = Qt.UserRole + 8

    countChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._ids: list[str] = []
        self._instances: dict[str, Instance] = {}

    def roleNames(self):
        return {
            self.IdRole: b"instanceId",
            self.NameRole: b"name",
            self.VersionRole: b"version",
            self.ModloaderRole: b"modloader",
            self.ModloaderVersionRole: b"modloaderVersion",
            self.LastPlayedRole: b"lastPlayed",
            self.PlaytimeRole: b"playtime",
            self.IconRole: b"icon",
        }

    def rowCount(self, parent=QModelIndex()):
        return len(self._ids)

    def data(self, index: QModelIndex, role: int):
        if not index.isValid() or not (0 <= index.row() < len(self._ids)):
            return None

        instance_id = self._ids[index.row()]
        instance = self._instances[instance_id]

        if role == self.IdRole:
            return instance_id
        if role == self.NameRole:
            return instance.name
        if role == self.VersionRole:
            return instance.version
        if role == self.ModloaderRole:
            return MODLOADER_NAMES.get(instance.modloader, "Unknown")
        if role == self.ModloaderVersionRole:
            return instance.modloader_version
        if role == self.LastPlayedRole:
            return instance.last_played
        if role == self.PlaytimeRole:
            return instance.playtime
        if role == self.IconRole:
            return instance.icon

        return None

    def set_instances(self, instances: dict[str, Instance]):
        self.beginResetModel()
        self._ids = list(instances.keys())
        self._instances = instances
        self.endResetModel()
        self.countChanged.emit()