if 0:
    from .general_screen import ToolDeltaScreen

# Really useful?


active_tooldelta_screens = {}  # type: dict[str, ToolDeltaScreen]


def _addActiveToolDeltaScreen(screen):
    # type: (ToolDeltaScreen) -> None
    active_tooldelta_screens[screen._screen_name] = screen


def _removeActiveToolDeltaScreen(screen):
    # type: (ToolDeltaScreen) -> None
    active_tooldelta_screens.pop(screen._screen_name, None)


def GetActiveToolDeltaScreen(key):
    # type: (str) -> ToolDeltaScreen | None
    return active_tooldelta_screens.get(key)


def GetActiveToolDeltaScreens():
    # type: () -> list[ToolDeltaScreen]
    return list(active_tooldelta_screens.values())


__all__ = [
    "GetActiveToolDeltaScreen",
    "GetActiveToolDeltaScreens",
]
