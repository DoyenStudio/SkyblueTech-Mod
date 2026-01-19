# coding=utf-8
import mod.client.extraClientApi as clientApi
if 0:
    from typing import Callable, TypeVar
    FuncT = TypeVar("FuncT", bound=Callable[..., int | None])

ViewBinder = clientApi.GetViewBinderCls()


class UIPath(object):
    def __init__(self, base):
        # type: (str) -> None
        self.base = base

    def __truediv__(self, path):
        # type: (str) -> UIPath
        return UIPath(self.base + "/" + path)

    def __mod__(self, val):
        return self.base % val

    __div__ = __truediv__

    def __repr__(self):
        return self.base

    def __add__(self, path):
        # type: (str) -> UIPath
        return UIPath(self.base + path)

    def __hash__(self):
        return hash(self.base)


class Binder(ViewBinder):
    @classmethod
    def binding(cls, bind_flag, binding_name):
        # type: (int, str) -> Callable[[FuncT], FuncT]
        return ViewBinder.binding(bind_flag, binding_name) # pyright: ignore[reportReturnType]

    @classmethod
    def binding_collection(cls, bind_flag, collection_name, binding_name):
        # type: (int, str, str) -> Callable[[FuncT], FuncT]
        return ViewBinder.binding_collection(bind_flag, collection_name, binding_name) # pyright: ignore[reportReturnType]



SCREEN_BASE_PATH = UIPath(
    "/variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel"
)

__all__ = ["Binder", "UIPath", "SCREEN_BASE_PATH"]
