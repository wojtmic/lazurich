# This file is auto-generated

import slint
import typing

class ProgressStage:
    done: bool
    text: str

    def __init__(self, *, done: typing.Optional[bool] = None, text: typing.Optional[str] = None) -> None: ...


class Theme:
    background: slint.Color
    button: slint.Color
    dashboard_icon: slint.Image
    list_icon: slint.Image
    primary: slint.Color
    secondary: slint.Color
    settings_icon: slint.Image
    sidebar: slint.Color
    skin_icon: slint.Image
    text: slint.Color


class AppWindow(slint.Component):
    dev: bool
    git_hash: str
    launch_active: bool
    launch_progress: float
    launch_stage: str
    launch_stages: slint.Model[ProgressStage]
    open_folder: typing.Callable[[], None]
    open_theme_debug: typing.Callable[[], None]
    preview_progress: typing.Callable[[], None]
    Theme: Theme


