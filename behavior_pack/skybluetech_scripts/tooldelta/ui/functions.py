from ..no_runtime_typing import TYPE_CHECKING

# TYPE_CHECKING
if TYPE_CHECKING:
    from .screen_comp import UScreenNode
    from .proxy_screen import UScreenProxy
    ScreenLike = UScreenNode | UScreenProxy
    from mod.client.ui.controls.baseUIControl import BaseUIControl
# TYPE_CHECKING END

def addElement(screen, element_def_name, element_name, parent, force_update=True):
    # type: (ScreenLike, str, str, BaseUIControl | None, bool) -> BaseUIControl
    return screen.base.CreateChildControl(element_def_name, element_name, parent, force_update) # pyright: ignore[reportArgumentType]

def removeElement(screen, element):
    # type: (ScreenLike, BaseUIControl) -> bool
    return screen.base.RemoveChildControl(element)
