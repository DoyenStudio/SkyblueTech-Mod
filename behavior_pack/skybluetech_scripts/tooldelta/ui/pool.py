if 0:
    from .screen_comp import UScreenNode
    from .proxy_screen import UScreenProxy
    from .general_screen import ToolDeltaScreen

# Really useful?

active_screens = {} # type: dict[str, UScreenNode]
active_proxy_screens = {} # type: dict[str, UScreenProxy]
active_tooldelta_screens = {} # type: dict[str, ToolDeltaScreen]


def _addActiveScreen(screen):
    # type: (UScreenNode) -> None
    active_screens[screen._key] = screen

def _removeActiveScreen(screen):
    # type: (UScreenNode) -> None
    active_screens.pop(screen._key, None)

def GetActiveScreen(key):
    # type: (str) -> UScreenNode | ToolDeltaScreen | None
    return active_screens.get(key) or active_tooldelta_screens.get(key)

def GetActiveScreens():
    # type: () -> list[UScreenNode | ToolDeltaScreen]
    return list(active_screens.values()) + list(active_tooldelta_screens.values())


def _addActiveProxyScreen(proxy):
    # type: (UScreenProxy) -> None
    active_proxy_screens[proxy.screenName] = proxy

def _removeActiveProxyScreen(proxy):
    # type: (UScreenProxy) -> None
    active_proxy_screens.pop(proxy.screenName, None)

def GetActiveProxyScreen(key):
    # type: (str) -> UScreenProxy | None
    return active_proxy_screens.get(key)

def GetActiveProxyScreens():
    # type: () -> list[UScreenProxy]
    return list(active_proxy_screens.values())

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
    "GetActiveScreen",
    "GetActiveScreens",
    "GetActiveProxyScreen",
    "GetActiveProxyScreens",
]
