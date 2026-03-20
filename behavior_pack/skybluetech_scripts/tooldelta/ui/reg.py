# coding=utf-8
from mod.client.extraClientApi import RegisterUI, GetNativeScreenManagerCls
from mod_log import logger
from ..internal import GetModName
from ..events.client.ui import UiInitFinishedEvent


from .general_screen import ToolDeltaScreen
from .room import _regist_content

# TYPE_CHECKING
if 0:
    from typing import TypeVar

    ToolDeltaScreenT = TypeVar("ToolDeltaScreenT", bound="type[ToolDeltaScreen]")
# TYPE_CHECKING END


NSManagerIns = GetNativeScreenManagerCls().instance()  # type: ignore
registeredScreens = {}  # type: dict[str, type[ToolDeltaScreen]]
registeredToolDeltaScreenClasses = {}  # type: dict[str, tuple[type[ToolDeltaScreen], str, str, bool]]


def RegistToolDeltaScreen(
    bound_ui_name,  # type: str
    key=None,  # type: str | None
    is_proxy=False,
):
    key = key or bound_ui_name

    def wrapper(screen_cls):
        # type: (ToolDeltaScreenT) -> ToolDeltaScreenT
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
    # (UiInitFinishedEvent) -> None
    for ui_key, (
        screen_cls,
        cls_path,
        bound_ui_name,
        is_proxy,
    ) in registeredToolDeltaScreenClasses.items():
        if is_proxy:
            ui_base_cls = screen_cls._register_as_proxy(ui_key, bound_ui_name)
            path = _regist_content(ui_base_cls)
            NSManagerIns.RegisterScreenProxy(bound_ui_name, path)
        else:
            ui_base_cls = screen_cls._register_as_screen(ui_key)
            path = _regist_content(ui_base_cls)
            res = RegisterUI(GetModName(), ui_key, path, bound_ui_name)
            if not res:
                logger.error(
                    "RegisterUI failed: {}, {}".format(cls_path, bound_ui_name)
                )
        registeredScreens[ui_key] = screen_cls


__all__ = ["RegistToolDeltaScreen", "GetScreen"]
