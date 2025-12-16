# coding=utf-8
#
# from weakref import WeakValueDictionary
from mod.client.ui.screenNode import ScreenNode
from mod.client.ui.controls.baseUIControl import BaseUIControl
from mod.client.ui.controls.minimapUIControl import MiniMapUIControl
from mod.client.ui.controls.inputPanelUIControl import InputPanelUIControl
from mod.client.ui.controls.itemRendererUIControl import ItemRendererUIControl
from mod.client.ui.controls.neteaseComboBoxUIControl import NeteaseComboBoxUIControl
from mod.client.ui.controls.progressBarUIControl import ProgressBarUIControl
from mod.client.ui.controls.buttonUIControl import ButtonUIControl
from mod.client.ui.controls.switchToggleUIControl import SwitchToggleUIControl
from mod.client.ui.controls.imageUIControl import ImageUIControl
from mod.client.ui.controls.stackPanelUIControl import StackPanelUIControl
from mod.client.ui.controls.selectionWheelUIControl import SelectionWheelUIControl
from mod.client.ui.controls.textEditBoxUIControl import TextEditBoxUIControl
from mod.client.ui.controls.gridUIControl import GridUIControl
from mod.client.ui.controls.labelUIControl import LabelUIControl
from mod.client.ui.controls.neteasePaperDollUIControl import NeteasePaperDollUIControl
from mod.client.ui.controls.baseUIControl import BaseUIControl
from mod.client.ui.controls.scrollViewUIControl import ScrollViewUIControl
from mod.client.ui.controls.sliderUIControl import SliderUIControl
from ..api.timer import ExecLater
from ..api.client.ui import GetToggleMode
from ..events.client.ui import GridComponentSizeChangedClientEvent
from ..no_runtime_typing import TYPE_CHECKING
from .functions import addElement, removeElement

# TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Callable, Any, Literal
    from ..define.item import Item
    from .screen_comp import UScreenNode
    from .proxy_screen import UScreenProxy
    ScreenLike = UScreenNode | UScreenProxy
# TYPE_CHECKING END


class UBaseCtrl(object):
    def __init__(self, root, base):
        # type: (ScreenLike, BaseUIControl) -> None
        if base is None:
            raise ValueError("Can't initialize UBaseCtrl: comp is None")
        self._root = root
        self.base = base
        self._cache_t = None # type: Any | None
        self._child_cacher = {}
        self._vars = {}
        self._removed = False

    def SetVisible(self, visible, forceUpdate=True):
        # type: (bool, bool) -> None
        self.base.SetVisible(visible, forceUpdate)

    def AsLabel(self):
        # type: () -> ULabel
        return self._cache_t or self._save_t(ULabel(self._root, self.base.asLabel()))

    def AsButton(self):
        # type: () -> UButton
        return self._cache_t or self._save_t(UButton(self._root, self.base.asButton()))

    def AsItemRenderer(self):
        # type: () -> UItemRenderer
        return self._cache_t or self._save_t(UItemRenderer(self._root, self.base.asItemRenderer()))

    def AsImage(self):
        # type: () -> UImage
        return self._cache_t or self._save_t(UImage(self._root, self.base.asImage()))

    def AsScrollView(self):
        # type: () -> UScrollView
        return self._cache_t or self._save_t(UScrollView(self._root, self.base.asScrollView()))

    def AsGrid(self):
        # type: () -> UGrid
        return self._cache_t or self._save_t(UGrid(self._root, self.base.asGrid()))

    def AsSlider(self):
        # type: () -> USlider
        return self._cache_t or self._save_t(USlider(self._root, self.base.asSlider()))

    def getFullPath(self):
        "未开放接口"
        return self.base.FullPath() # type: ignore

    def SetFullPos(
        self,
        axis, # type: Literal["x", "y"]
        follow_type="none", # type: Literal["none", "parent", "maxChildren", "maxSibling", "children", "x", "y"]
        relative_value=0.0, # type: float
        absolute_value=0.0, # type: float
    ):
        return self.base.SetFullPosition(axis, {
            "followType": follow_type,
            "relativeValue": relative_value,
            "absoluteValue": absolute_value
        })

    def SetSize(self, xy):
        # type: (tuple[float, float]) -> None
        self.base.SetSize(xy)

    def SetFullSize(self, axis, params):
        # type: (str, dict) -> None
        self.base.SetFullSize(axis, params)

    def SetLayer(self, layer):
        # type: (int) -> None
        self.base.SetLayer(layer)

    def AddElement(self, element_def_name, element_name, force_update=True):
        # type: (str, str, bool) -> UBaseCtrl
        return UBaseCtrl(self._root, addElement(self._root, element_def_name, element_name, self.base, force_update))

    def OnDestroyed(self):
        pass

    def Remove(self):
        if self._removed:
            print("[Warning] control already removed")
            return
        self._removed = True
        return removeElement(self._root, self.base)

    def __truediv__(self, path):
        # type: (str) -> UBaseCtrl
        return self._get_path_cache(path)

    __getitem__ = __div__ = __truediv__

    def callDestroy(self):
        self.OnDestroyed()

    def _save_t(self, obj):
        self._cache_t = obj
        return obj

    def _get_path_cache(self, path):
        if path not in self._child_cacher:
            self._child_cacher[path] = UBaseCtrl(self._root, self.base.GetChildByPath("/" + path))
        return self._child_cacher[path]


class UItemRenderer(UBaseCtrl):
    def __init__(self, root, base):
        # type: (ScreenLike, ItemRendererUIControl) -> None
        UBaseCtrl.__init__(self, root, base)
        if not isinstance(base, ItemRendererUIControl):
            raise TypeError(
                "expected ItemRendererUIControl, got " + str(type(base))
            )
        self.base = base

    def SetUiItem(self, item):
        # type: (Item) -> None
        self.base.SetUiItem(item.newItemName, item.newAuxValue, item.isEnchanted, item.userData or {})


class ULabel(UBaseCtrl):
    def __init__(self, root, base):
        # type: (ScreenLike, LabelUIControl) -> None
        UBaseCtrl.__init__(self, root, base)
        if not isinstance(base, LabelUIControl):
            raise TypeError(
                "expected LabelUIControl, got " + str(type(base))
            )
        self.base = base

    def SetText(self, text):
        # type: (str) -> None
        self.base.SetText(text)

    def GetText(self):
        # type: () -> str | None
        return self.base.GetText()


class UImage(UBaseCtrl):
    def __init__(self, root, base):
        # type: (ScreenLike, ImageUIControl) -> None
        UBaseCtrl.__init__(self, root, base)
        if not isinstance(base, ImageUIControl):
            raise TypeError(
                "expected ImageUIControl, got " + str(type(base))
            )
        self.base = base

    def SetSprite(self, sprite_path):
        # type: (str) -> None
        self.base.SetSprite(sprite_path)

    def SetSpriteColor(self, rgb):
        # type: (tuple[float, float, float]) -> None
        self.base.SetSpriteColor(rgb)

    def SetSpriteClipRatio(self, clipDirection, clipRatio):
        # type: (str, float) -> None
        self.base.SetClipDirection(clipDirection)
        self.base.SetSpriteClipRatio(clipRatio)


class UButton(UBaseCtrl):
    def __init__(self, root, base):
        # type: (ScreenLike, ButtonUIControl) -> None
        UBaseCtrl.__init__(self, root, base)
        if not isinstance(base, ButtonUIControl):
            raise TypeError(
                "expected ButtonUIControl, got " + str(type(base))
            )
        self.base = base

    def SetCallback(self, callback):
        # type: (Callable[[Any], None]) -> None
        self.base.AddTouchEventParams({"isSwallow": True})
        self.base.SetButtonTouchUpCallback(callback) # pyright: ignore[reportArgumentType]

    def SetOnRollOverCallback(self, callback):
        # type: (Callable[[dict], None]) -> None
        self.base.AddHoverEventParams()
        self.base.SetButtonHoverInCallback(callback) # pyright: ignore[reportArgumentType]

    def SetOnRollOutCallback(self, callback):
        # type: (Callable[[dict], None]) -> None
        self.base.AddHoverEventParams()
        self.base.SetButtonHoverOutCallback(callback) # pyright: ignore[reportArgumentType]


class UScrollView(UBaseCtrl):
    def __init__(self, root, base):
        # type: (ScreenLike, ScrollViewUIControl) -> None
        UBaseCtrl.__init__(self, root, base)
        if not isinstance(base, ScrollViewUIControl):
            raise TypeError(
                "expected ScrollViewUIControl, got " + str(type(base))
            )
        self.base = base

    def GetContent(self):
        if GetToggleMode() == 0:
            scroll_device = "scroll_mouse"
        else:
            scroll_device = "scroll_touch"
        return self[scroll_device + "/scroll_view/stack_panel/background_and_viewport/scrolling_view_port/scrolling_content"]


class UGrid(UBaseCtrl):
    def __init__(self, root, base):
        # type: (ScreenLike, GridUIControl) -> None
        UBaseCtrl.__init__(self, root, base)
        if not isinstance(base, GridUIControl):
            raise TypeError(
                "expected GridUIControl, got " + str(type(base))
            )
        self.path = self.base.GetPath()
        grid_comp_size_changed_cbs[self.path] = self.onGridSizeChanged
        self.later_exec_cbs = [] # type: list[Callable[[], None]]
        self.base = base

    def GetGridDimension(self):
        " 未开放接口 "
        import gui # pyright: ignore[reportMissingImports]
        return gui.get_grid_dimension(self._root.base.GetScreenName(), self.getFullPath())

    def GetGridItem(self, x, y):
        # type: (int, int) -> UBaseCtrl
        return UBaseCtrl(self._root, self.base.GetGridItem(x, y))

    def SetGridDimension(self, xy):
        # type: (tuple[int, int]) -> None
        self.base.SetGridDimension(xy)

    def ExecuteAfterUpdate(self, cb):
        # type: (Callable[[], None]) -> None
        self.later_exec_cbs.append(cb)

    def onGridSizeChanged(self):
        try:
            for cb in self.later_exec_cbs:
                cb()
        finally:
            self.later_exec_cbs = []

    def OnDestroyed(self):
        UBaseCtrl.OnDestroyed(self)
        grid_comp_size_changed_cbs.pop(self.base.GetPath(), None)


class UComboBox(UBaseCtrl):
    def __init__(self, root, base):
        # type: (ScreenLike, NeteaseComboBoxUIControl) -> None
        UBaseCtrl.__init__(self, root, base)
        if not isinstance(base, NeteaseComboBoxUIControl):
            raise TypeError(
                "expected NeteaseComboBoxUIControl, got " + str(type(base))
            )
        self.base = base

    def AddOption(self, text, icon=None, extra_data=None):
        self.base.AddOption(text, icon, extra_data)

    def Clear(self):
        self.base.ClearOptions()

    def ClearSelection(self):
        self.base.ClearSelection()

    def GetOptionCount(self):
        return self.base.GetOptionCount()

    def GetSelectedOption(self):
        return self.base.GetSelectOptionIndex()


class USlider(UBaseCtrl):
    def __init__(self, root, base):
        # type: (ScreenLike, SliderUIControl) -> None
        UBaseCtrl.__init__(self, root, base)
        if not isinstance(base, SliderUIControl):
            raise TypeError(
                "expected SliderUIControl, got " + str(type(base))
            )
        self.base = base

    def GetSliderValue(self):
        return self.base.GetSliderValue()

    def SetSliderValue(self, value):
        # type: (float) -> None
        self.base.SetSliderValue(value)


class UNeteasePaperDoll(UBaseCtrl):
    def __init__(self, root, base):
        # type: (ScreenLike, NeteasePaperDollUIControl) -> None
        UBaseCtrl.__init__(self, root, base)
        if not isinstance(base, NeteasePaperDollUIControl):
            raise TypeError(
                "expected NeteasePaperDollUIControl, got " + str(type(base))
            )
        self.base = base

    def RenderEntity(
        self,
        entity_id=None, # type: str | None
        entity_identifier=None, # type: str | None
        scale=1.0, # type: float
        render_depth=-50, # type: int
        init_rot_x=0, # type: float
        init_rot_y=0, # type: float
        init_rot_z=0, # type: float
        molang_dict={}, # type: dict
        rotation_axis=(0, 0, 0), # type: tuple[int, int, int]
    ):
        self.base.RenderEntity({
            "entity_id": entity_id,
            "entity_identifier": entity_identifier,
            "scale": scale,
            "render_depth": render_depth,
            "init_rot_x": init_rot_x,
            "init_rot_y": init_rot_y,
            "init_rot_z": init_rot_z,
            "molang_dict": molang_dict,
            "rotation_axis": rotation_axis,
        })


grid_comp_size_changed_cbs = dict() # type: dict[str, Callable[[], None]]

@GridComponentSizeChangedClientEvent.Listen()
def onGridComponentSizeChanged(event):
    # type: (GridComponentSizeChangedClientEvent) -> None
    path = event.path
    if path.startswith("/main"):
        path = path[5:]
    cb = grid_comp_size_changed_cbs.get(path)
    if cb:
        ExecLater(0, cb) # TODO: 不知道为什么 如果直接 cb() grid 会获取不到新 position。。


__all__ = [
    "UBaseCtrl",
    "UItemRenderer",
    "ULabel",
    "UImage",
    "UButton"
]