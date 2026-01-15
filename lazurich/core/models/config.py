from dataclasses import dataclass

@dataclass
class CoreConfig:
    advanced_mode: bool = False
    dev_mode     : bool = False
    downloads    : int = 5

@dataclass
class GUIConfig:
    qt_theme     : str = 'default'

@dataclass
class DevConfig:
    allow_dangerous_paste: bool = False
