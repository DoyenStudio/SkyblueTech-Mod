# coding=utf-8
from mod.client.extraClientApi import RegisterUI, GetNativeScreenManagerCls
from mod_log import logger
from ..internal import GetModName
from ..events.client.ui import UiInitFinishedEvent
from ..no_runtime_typing import TYPE_CHECKING
from .screen_comp import UScreenNode
from .proxy_screen import UScreenProxy

# TYPE_CHECKING
if TYPE_CHECKING:
    from typing import TypeVar
    from mod.client.extraClientApi import NativeScreenManager
    
    UScreenNodeT = TypeVar('UScreenNodeT', bound=type[UScreenNode])
    UScreenProxyT = TypeVar('UScreenProxyT', bound=type[UScreenProxy])
# TYPE_CHECKING END


NSManagerIns = GetNativeScreenManagerCls().instance() # type: NativeScreenManager # type: ignore
registeredScreens = {} # type: dict[str, type[UScreenNode]]
registeredScreenDatas = {} # type: dict[str, tuple[str, str]]
registeredScreensProxy = {} # type: dict[str, type[UScreenProxy]]


def GetScreenClsKey(screen_cls):
    # type: (type[UScreenNode]) -> str
    return "tdui:{}.{}".format(screen_cls.__module__, screen_cls.__name__)

def RegistScreen(
    bound_ui=None # type: str | None
):
    def wrapper(screen_cls):
        # type: (UScreenNodeT) -> UScreenNodeT
        _bound_ui = bound_ui or screen_cls.bound_ui
        if _bound_ui is None:
            raise ValueError("bound_ui is None")
        key = screen_cls._key = GetScreenClsKey(screen_cls)
        if key in registeredScreens:
            logger.warning("ToolDelta: Screen key {} already exists. Abort".format(key))
            return screen_cls
        registeredScreens[key] = screen_cls
        cls_path = screen_cls.__module__ + "." + screen_cls.__name__
        registeredScreenDatas[key] = (cls_path, _bound_ui)
        return screen_cls
    return wrapper

def RegistProxyScreen(
    bound_ui_name=None # type: str | None
):
    def wrapper(proxy_screen_cls):
        # type: (UScreenProxyT) -> UScreenProxyT
        proxy_screen_cls.bound_proxier = bound_ui_name or proxy_screen_cls.bound_proxier
        if proxy_screen_cls in registeredScreensProxy.values():
            logger.warning("ToolDelta: Proxy screen {} already exists. Abort".format(proxy_screen_cls))
            return proxy_screen_cls
        cls_path = proxy_screen_cls.__module__ + "." + proxy_screen_cls.__name__
        registeredScreensProxy[cls_path] = proxy_screen_cls
        return proxy_screen_cls
    return wrapper

def GetScreen(key):
    return registeredScreens.get(key)

@UiInitFinishedEvent.Listen(1000)
def onUiInit(_):
    for key, (cls_path, bound_ui) in registeredScreenDatas.items():
        res = RegisterUI(
            GetModName(),
            key, cls_path,
            bound_ui
        )
        if not res:
            logger.error("RegisterUI failed: {}, {}".format(cls_path, bound_ui))
    for cls_path, proxy_screen_cls in registeredScreensProxy.items():
        NSManagerIns.RegisterScreenProxy(proxy_screen_cls.bound_proxier, cls_path)
    logger.debug("Screen registered")

__all__ = [
    "RegistScreen",
    "RegistProxyScreen",
    "GetScreen",
    "GetScreenClsKey"
]