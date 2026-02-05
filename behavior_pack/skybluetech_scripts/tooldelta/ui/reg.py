# coding=utf-8
from mod.client.extraClientApi import RegisterUI, GetNativeScreenManagerCls
from mod_log import logger
from ..internal import GetModName
from ..events.client.ui import UiInitFinishedEvent

from .screen_comp import UScreenNode
from .proxy_screen import UScreenProxy
from .general_screen import ToolDeltaScreen
from .room import _regist_content

# TYPE_CHECKING
if 0:
    from typing import TypeVar
    from mod.client.extraClientApi import NativeScreenManager

    UScreenNodeT = TypeVar("UScreenNodeT", bound=type[UScreenNode])
    UScreenProxyT = TypeVar("UScreenProxyT", bound=type[UScreenProxy])
    UToolDeltaScreenT = TypeVar("UToolDeltaScreenT", bound=type[ToolDeltaScreen])
# TYPE_CHECKING END


NSManagerIns = GetNativeScreenManagerCls().instance()  # type: NativeScreenManager # type: ignore
registeredScreens = {}  # type: dict[str, type[UScreenNode | ToolDeltaScreen]]
registeredScreenClasses = {}  # type: dict[str, tuple[type[UScreenNode], str, str]]
registeredScreenProxyClasses = {}  # type: dict[str, type[UScreenProxy]]
registeredToolDeltaScreenClasses = {}  # type: dict[str, tuple[type[ToolDeltaScreen], str, str, bool]]


# def GetScreenClsKey(screen_cls):
#     # type: (type[UScreenNode]) -> str
#     return "tdui:{}.{}".format(screen_cls.__module__, screen_cls.__name__)


def RegistScreen(
    bound_ui,  # type: str
    key=None,  # type: str | None
):
    def wrapper(screen_cls):
        # type: (UScreenNodeT) -> UScreenNodeT
        ui_key = key or bound_ui
        screen_cls._key = ui_key
        if ui_key in registeredScreenClasses:
            logger.warning(
                "ToolDelta: Screen key {} already exists. Abort".format(ui_key)
            )
            return screen_cls
        cls_path = screen_cls.__module__ + "." + screen_cls.__name__
        registeredScreenClasses[ui_key] = (screen_cls, cls_path, bound_ui)
        return screen_cls

    return wrapper


def RegistProxyScreen(
    bound_ui_name=None,  # type: str | None
):
    def wrapper(proxy_screen_cls):
        # type: (UScreenProxyT) -> UScreenProxyT
        proxy_screen_cls.bound_proxier = bound_ui_name or proxy_screen_cls.bound_proxier
        if proxy_screen_cls in registeredScreenProxyClasses.values():
            logger.warning(
                "ToolDelta: Proxy screen {} already exists. Abort".format(
                    proxy_screen_cls
                )
            )
            return proxy_screen_cls
        cls_path = proxy_screen_cls.__module__ + "." + proxy_screen_cls.__name__
        registeredScreenProxyClasses[cls_path] = proxy_screen_cls
        return proxy_screen_cls

    return wrapper


def RegistToolDeltaScreen(
    bound_ui_name,  # type: str
    key=None,  # type: str | None
    is_proxy=False,
):
    key = key or bound_ui_name

    def wrapper(screen_cls):
        # type: (UToolDeltaScreenT) -> UToolDeltaScreenT
        if bound_ui_name in registeredToolDeltaScreenClasses.values():
            logger.warning(
                "ToolDelta: screen {} already exists. Abort".format(screen_cls)
            )
            return screen_cls
        screen_cls._screen_key = key
        cls_path = screen_cls.__module__ + "." + screen_cls.__name__ + "_Base"
        registeredToolDeltaScreenClasses[key] = (
            screen_cls,
            cls_path,
            bound_ui_name,
            is_proxy,
        )
        return screen_cls

    return wrapper


def GetScreen(key):
    return registeredScreens.get(key)


@UiInitFinishedEvent.Listen(10)
def onUiInit(_):
    for key, (ui_cls, cls_path, bound_ui) in registeredScreenClasses.items():
        res = RegisterUI(GetModName(), key, cls_path, bound_ui)
        if not res:
            logger.error("RegisterUI failed: {}, {}".format(cls_path, bound_ui))
        registeredScreens[key] = ui_cls
    for cls_path, proxy_screen_cls in registeredScreenProxyClasses.items():
        NSManagerIns.RegisterScreenProxy(proxy_screen_cls.bound_proxier, cls_path)
    for key, (
        screen_cls,
        cls_path,
        bound_ui,
        is_proxy,
    ) in registeredToolDeltaScreenClasses.items():
        if is_proxy:
            ui_base_cls = screen_cls._register_as_proxy(key, bound_ui)
            path = _regist_content(ui_base_cls)
            NSManagerIns.RegisterScreenProxy(bound_ui, path)
        else:
            ui_base_cls = screen_cls._register_as_screen(key, bound_ui)
            path = _regist_content(ui_base_cls)
            res = RegisterUI(GetModName(), key, path, bound_ui)
            if not res:
                logger.error("RegisterUI failed: {}, {}".format(cls_path, bound_ui))
        registeredScreens[key] = screen_cls


__all__ = ["RegistScreen", "RegistProxyScreen", "RegistToolDeltaScreen", "GetScreen"]
