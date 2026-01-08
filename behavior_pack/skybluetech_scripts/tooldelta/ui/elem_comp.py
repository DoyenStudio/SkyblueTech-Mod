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
from ..define import UICtrlPosData, Item
from ..api.timer import ExecLater
from ..api.client.ui import GetToggleMode
from ..events.client.ui import GridComponentSizeChangedClientEvent
from ..no_runtime_typing import TYPE_CHECKING
from .functions import addElement, removeElement
from .utils import SNode

# TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Callable, Any, Literal
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
        self._removed_listeners = [] # type: list[Callable[[], None]]

    def asLabel(self):
        # type: () -> ULabel
        return self._cache_t or self._save_t(ULabel(self._root, self.base.asLabel()))

    def asButton(self):
        # type: () -> UButton
        return self._cache_t or self._save_t(UButton(self._root, self.base.asButton()))

    def asItemRenderer(self):
        # type: () -> UItemRenderer
        return self._cache_t or self._save_t(UItemRenderer(self._root, self.base.asItemRenderer()))

    def asImage(self):
        # type: () -> UImage
        return self._cache_t or self._save_t(UImage(self._root, self.base.asImage()))

    def asScrollView(self):
        # type: () -> UScrollView
        return self._cache_t or self._save_t(UScrollView(self._root, self.base.asScrollView()))

    def asGrid(self):
        # type: () -> UGrid
        return self._cache_t or self._save_t(UGrid(self._root, self.base.asGrid()))

    def asSlider(self):
        # type: () -> USlider
        return self._cache_t or self._save_t(USlider(self._root, self.base.asSlider()))

    def asNeteasePaperDoll(self):
        # type: () -> UNeteasePaperDoll
        return self._cache_t or self._save_t(UNeteasePaperDoll(self._root, self.base.asNeteasePaperDoll()))

    def asTextEditBox(self):
        # type: () -> UTextEditBoxUIControl
        return self._cache_t or self._save_t(UTextEditBoxUIControl(self._root, self.base.asTextEditBox()))

    def getFullPath(self):
        "未开放接口"
        return self.base.FullPath() # type: ignore

    def GetSize(self):
        # type: () -> tuple[float, float]
        return self.base.GetSize()

    def GetPropertyBag(self):
        # type: () -> dict
        return self.base.GetPropertyBag()

    def GetPos(self):
        # type: () -> tuple[float, float]
        return self.base.GetPosition()

    def GetRootPos(self):
        # type: () -> tuple[float, float]
        return self.base.GetGlobalPosition()

    def GetFullPos(self, axis):
        # type: (Literal["x", "y"]) -> UICtrlPosData
        return UICtrlPosData.from_dict(self.base.GetFullPosition(axis))

    def SetFullPos(
        self,
        axis, # type: Literal["x", "y"]
        posdata, # type: UICtrlPosData
    ):
        return self.base.SetFullPosition(axis, posdata.marshal())

    def SetVisible(self, visible, forceUpdate=True):
        # type: (bool, bool) -> None
        self.base.SetVisible(visible, forceUpdate)

    def SetPropertyBag(self, params):
        # type: (dict) -> bool
        return self.base.SetPropertyBag(params)

    def SetPos(self, xy):
        # type: (tuple[float, float]) -> None
        self.base.SetPosition(xy)

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

    def addDestroyListener(self, func):
        # type: (Callable[[], None]) -> None
        self._removed_listeners.append(func)

    def OnDestroyed(self):
        pass

    def Remove(self):
        if self._removed:
            print("[Warning] control already removed")
            return False
        self._removed = True
        self.callDestroy()
        return removeElement(self._root, self.base)

    def GetElement(self, path):
        # type: (str | SNode) -> UBaseCtrl
        return self._get_path_cache(path)

    # ====

    def __truediv__(self, path):
        # type: (str) -> UBaseCtrl
        return self._get_path_cache(path)

    __getitem__ = __div__ = __truediv__

    def callDestroy(self):
        for func in self._removed_listeners:
            func()
        self.OnDestroyed()

    def _save_t(self, obj):
        self._cache_t = obj
        return obj

    def _get_path_cache(self, path):
        if isinstance(path, SNode):
            path = path.base
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

    def GetUiItem(self):
        # type: () -> tuple[str, int, bool]
        res = self.base.GetUiItem()
        return res["itemName"], res["auxValue"], res["isEnchanted"]


class ULabel(UBaseCtrl):
    def __init__(self, root, base):
        # type: (ScreenLike, LabelUIControl) -> None
        UBaseCtrl.__init__(self, root, base)
        if not isinstance(base, LabelUIControl):
            raise TypeError(
                "expected LabelUIControl, got " + str(type(base))
            )
        self.base = base

    def SetText(self, text, sync_size=False):
        # type: (str, bool) -> None
        self.base.SetText(text, sync_size)

    def GetText(self):
        # type: () -> str | None
        return self.base.GetText()

    def SetColor(self, rgb):
        # type: (tuple[float, float, float]) -> None
        self.base.SetTextColor(rgb)


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
        # type: (Literal["fromLeftToRight", "fromRightToLeft", "fromTopToBottom", "fromBottomToTop", "fromOutsideToInside"], float) -> None
        self.base.SetClipDirection(clipDirection)
        self.base.SetSpriteClipRatio(clipRatio)

    def SetUV(self, uv, uv_size):
        # type: (tuple[float, float], tuple[float, float]) -> None
        self.base.SetSpriteUV(uv)
        self.base.SetSpriteUVSize(uv_size)


class UButton(UBaseCtrl):
    def __init__(self, root, base):
        # type: (ScreenLike, ButtonUIControl) -> None
        UBaseCtrl.__init__(self, root, base)
        if not isinstance(base, ButtonUIControl):
            raise TypeError(
                "expected ButtonUIControl, got " + str(type(base))
            )
        self.base = base

    def SetCallback(
        self,
        callback # type: Callable[[Any], None]
    ):
        self.base.AddTouchEventParams({"isSwallow": True})
        self.base.SetButtonTouchUpCallback(callback) # pyright: ignore[reportArgumentType]
        return self

    def SetOnRollOverCallback(
        self,
        callback # type: Callable[[dict], None]
    ):
        self.base.AddHoverEventParams()
        self.base.SetButtonHoverInCallback(callback) # pyright: ignore[reportArgumentType]
        return self

    def SetOnRollOutCallback(
        self,
        callback # type: Callable[[dict], None]
    ):
        self.base.AddHoverEventParams()
        self.base.SetButtonHoverOutCallback(callback) # pyright: ignore[reportArgumentType]
        return self


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
        # type: () -> tuple[int, int]
        " 未开放接口 "
        import gui # pyright: ignore[reportMissingImports]
        return gui.get_grid_dimension(self._root.base.GetScreenName(), self.getFullPath())

    def GetGridItem(self, x, y):
        # type: (int, int) -> UBaseCtrl
        return UBaseCtrl(self._root, self.base.GetGridItem(x, y))

    def SetGridDimension(self, xy):
        # type: (tuple[int, int]) -> None
        self.base.SetGridDimension(xy)

    def SetDimensionAndCall(self, xy, cb):
        # type: (tuple[int, int], Callable[[], None]) -> None
        old_xy = self.GetGridDimension()
        if xy == old_xy:
            cb()
        else:
            self.SetGridDimension(xy)
            self.ExecuteAfterUpdate(cb)

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
        rotation_axis=(0, 0, 0), # type: tuple[Literal[0, 1], Literal[0, 1], Literal[0, 1]]
    ):
        return self.base.RenderEntity({
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

    def RenderBlockGeometryModel(
        self,
        block_geometry_model_name, # type: str
        scale=1.0, # type: float
        init_rot_y=0, # type: float
        init_rot_x=0, # type: float
        init_rot_z=0, # type: float
        molang_dict=None, # type: dict | None
        rotation_axis=(1, 0, 0), # type: tuple[Literal[0, 1], Literal[0, 1], Literal[0, 1]]
    ):
        return self.base.RenderBlockGeometryModel({
            "block_geometry_model_name": block_geometry_model_name,
            "scale": scale,
            "init_rot_y": init_rot_y,
            "init_rot_x": init_rot_x,
            "init_rot_z": init_rot_z,
            "molang_dict": molang_dict or {},
            "rotation_axis": rotation_axis,
        })


class UTextEditBoxUIControl(UBaseCtrl):
    def __init__(self, root, base):
        # type: (ScreenLike, TextEditBoxUIControl) -> None
        UBaseCtrl.__init__(self, root, base)
        if not isinstance(base, TextEditBoxUIControl):
            raise TypeError(
                "expected TextEditBoxUIControl, got " + str(type(base))
            )
        self.base = base

    def GetText(self):
        return self.base.GetEditText()

    def SetText(self, text):
        # type: (str) -> None
        self.base.SetEditText(text)


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