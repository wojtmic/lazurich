import asyncio
import functools
from typing import Callable

from PySide6.QtCore import QObject, Slot


class _ButtonBridge(QObject):
    """Holds the registered handlers and gets exposed to QML."""

    def __init__(self):
        super().__init__()
        self._handlers: dict[str, Callable] = {}

    def register(self, button_id: str, coro_fn: Callable):
        self._handlers[button_id] = coro_fn

    @Slot(str)
    def trigger(self, button_id: str):
        handler = self._handlers.get(button_id)
        if handler is None:
            return
        asyncio.ensure_future(handler())


_bridge = _ButtonBridge()


def get_bridge() -> _ButtonBridge:
    return _bridge


def on_button_press(button_id: str):
    def decorator(coro_fn: Callable):
        _bridge.register(button_id, coro_fn)

        @functools.wraps(coro_fn)
        def wrapper(*args, **kwargs):
            return coro_fn(*args, **kwargs)

        return wrapper

    return decorator