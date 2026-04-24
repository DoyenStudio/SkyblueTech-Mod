# coding=utf-8
#
from weakref import WeakSet, ref
from ..define import UICtrlPosData, Item
from ..api.common import ExecLater
from ..events.client.ui import GridComponentSizeChangedClientEvent
from .utils import UIPath

# TYPE_CHECKING
if 0:
    from typing import Callable, Any, Literal
    from .general_screen import ToolDeltaScreen
    from ._ui_typing import *
# TYPE_CHECKING END


class UBaseCtrl(object):
    def __init__(self, root, base):
        # type: (ToolDeltaScreen, BaseUIControl | None) -> None
        if base is None:
            raise ValueError("Can't initialize UBaseCtrl: comp is None")
        self._root = root
        self._parent_cached = None
        self.base = base
        self._cache_t = None  # type: Any | None
        self._vars = {}
        self._removed = False
        self._bind_objectref = None # type: ref | None
        self._removed_listeners = []  # type: list[Callable[[], None]]
        self._sub_ctrls = WeakSet()  # type: WeakSet[UBaseCtrl]
        root._add_sub_ctrl(self)

    def asLabel(self):
        # type: () -> ULabel
        return self._cache_t or self._save_t(ULabel(self._root, self.base.asLabel()))

    def asButton(self):
        # type: () -> UButton
        return self._cache_t or self._save_t(UButton(self._root, self.base.asButton()))

    def asItemRenderer(self):
        # type: () -> UItemRenderer
        return self._cache_t or self._save_t(
            UItemRenderer(self._root, self.base.asItemRenderer())
        )

    def asImage(self):
        # type: () -> UImage
        return self._cache_t or self._save_t(UImage(self._root, self.base.asImage()))

    def asScrollView(self):
        # type: () -> UScrollView
        return self._cache_t or self._save_t(
            UScrollView(self._root, self.base.asScrollView())
        )

    def asGrid(self):
        # type: () -> UGrid
        return self._cache_t or self._save_t(UGrid(self._root, self.base.asGrid()))

    def asSlider(self):
        # type: () -> USlider
        return self._cache_t or self._save_t(USlider(self._root, self.base.asSlider()))

    def asNeteasePaperDoll(self):
        # type: () -> UNeteasePaperDoll
        return self._cache_t or self._save_t(
            UNeteasePaperDoll(self._root, self.base.asNeteasePaperDoll())
        )

    def asTextEditBox(self):
        # type: () -> UTextEditBoxUIControl
        return self._cache_t or self._save_t(
            UTextEditBoxUIControl(self._root, self.base.asTextEditBox())
        )

    def asSwitch(self):
        # type: () -> USwitch
        return self._cache_t or self._save_t(
            USwitch(self._root, self.base.asSwitchToggle())
        )

    def clone(
        self,
        new_name,  # type: str
    ):
        this_path = self.getFullPath()
        parent_path = UIPath(this_path).parent
        ok = self._root.base.Clone(this_path, str(parent_path), new_name)
        if not ok:
            raise RuntimeError("Can't clone UI element to %s" % new_name)
        new_control_converter = CONVERT_MAP.get(self.__class__)
        if new_control_converter is None:
            raise RuntimeError(
                "Can't clone %s due to convert map lack" % self.__class__.__name__
            )
        return self.__class__(
            self._root,
            new_control_converter(self._root.GetBaseUIControl(parent_path / new_name)),
        )

    def getFullPath(self):
        "未开放接口"
        return self.base.FullPath()  # type: ignore

    @classmethod
    def convertFrom(
        cls,
        base_ui_control,  # type: BaseUIControl
    ):
        "将原版 BaseUIControl 转换为 UBaseCtrl"
        from .general_screen import ToolDeltaScreen

        return cls(ToolDeltaScreen.convertFrom(base_ui_control.mNode), base_ui_control)

    def GetVisible(self):
        # type: () -> bool
        return self.base.GetVisible()

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
        axis,  # type: Literal["x", "y"]
        posdata,  # type: UICtrlPosData
    ):
        return self.base.SetFullPosition(axis, posdata.to_dict())

    def SetVisible(self, visible, forceUpdate=True):
        # type: (bool, bool) -> None
        self.base.SetVisible(visible, forceUpdate)

    def SetPropertyBag(self, params):
        # type: (dict) -> bool
        return self.base.SetPropertyBag(params)

    def SetAnchorFrom(self, anchor):
        # type: (Literal["top_left", "top_middle", "top_right", "left_middle", "center", "right_middle", "bottom_left", "bottom_middle", "bottom_right"]) -> bool
        return self.base.SetAnchorFrom(anchor)

    def SetAnchorTo(self, anchor):
        # type: (Literal["top_left", "top_middle", "top_right", "left_middle", "center", "right_middle", "bottom_left", "bottom_middle", "bottom_right"]) -> bool
        return self.base.SetAnchorTo(anchor)

    def SetPos(
        self,
        xy,  # type: tuple[float, float]
    ):
        self.base.SetPosition(xy)
        return self

    def SetAlpha(
        self,
        alpha,  # type: float
    ):
        self.base.SetAlpha(alpha)
        return self

    def SetSize(
        self,
        xy,  # type: tuple[float, float]
        resize_children=False,
    ):
        self.base.SetSize(xy, resize_children)
        return self

    def SetFullSize(
        self,
        axis,  # type: Literal["x", "y"]
        params,  # type: UICtrlPosData
    ):
        return self.base.SetFullSize(axis, params.to_dict())

    def SetLayer(
        self,
        layer,  # type: int
    ):
        self.base.SetLayer(layer)
        return self

    def AddElement(self, element_def_name, element_name, force_update=True):
        # type: (str, str, bool) -> UBaseCtrl
        ctrl = self._root.AddElement(
            element_def_name, element_name, force_update, _parent=self
        )
        self._sub_ctrls.add(ctrl)
        return ctrl

    def Remove(self, warning=True):
        # type: (bool) -> bool
        if self._removed and warning:
            print("[Warning] control already removed")
            return False
        self._call_destroy(top=True)
        return self._root._remove_sub_ctrl(self, from_top_removal=True)
    
    def BindLifeToObject(self, obj):
        # type: (object) -> None
        self._bind_objectref = ref(obj, lambda _:self.Remove(warning=False))

    def addDestroyListener(self, func):
        # type: (Callable[[], None]) -> None
        self._removed_listeners.append(func)

    def OnDestroyed(self):
        pass

    def GetElement(self, path):
        # type: (str | UIPath) -> UBaseCtrl
        if isinstance(path, UIPath):
            path = path.base
        ctrl = UBaseCtrl(self._root, self.base.GetChildByPath("/" + path))
        self._sub_ctrls.add(ctrl)
        return ctrl

    # ====

    @property
    def _parent(self):
        # type: () -> UBaseCtrl
        if self._parent_cached is None:
            parent_path = UIPath(self.getFullPath()).parent
            if not parent_path.base:
                raise ValueError("Parent is ScreenNode")
            self._parent_cached = self._root.GetElement(parent_path)
        return self._parent_cached

    def __truediv__(self, path):
        # type: (str) -> UBaseCtrl
        return self.GetElement(path)

    def __hash__(self):
        return hash(self.base.GetPath())
    
    __getitem__ = __div__ = __truediv__

    def _call_destroy(self, top=False):
        for func in self._removed_listeners:
            func()
        # for sub_ctrl in self._sub_ctrls:
        #     sub_ctrl._call_destroy(top=False)
        if self._removed:
            print("[Warning] element._call_destroy removed already!!!")
        else:
            if not top:
                self._root._remove_sub_ctrl(self, from_top_removal=False)
            self._removed = True
        self.OnDestroyed()

    def _save_t(self, obj):
        self._cache_t = obj
        return obj


class UItemRenderer(UBaseCtrl):
    def __init__(self, root, base):
        # type: (ToolDeltaScreen, ItemRendererUIControl | None) -> None
        UBaseCtrl.__init__(self, root, base)
        if base is None:
            raise TypeError("expected ItemRendererUIControl, got " + str(type(base)))
        self.base = base

    def SetUiItem(self, item):
        # type: (Item) -> bool
        return self.base.SetUiItem(
            item.newItemName, item.newAuxValue, item.isEnchanted, item.userData or {}
        )

    def GetUiItem(self):
        # type: () -> tuple[str, int, bool]
        res = self.base.GetUiItem()  # type: dict
        return res["itemName"], res["auxValue"], res["isEnchanted"]


class ULabel(UBaseCtrl):
    def __init__(self, root, base):
        # type: (ToolDeltaScreen, LabelUIControl | None) -> None
        UBaseCtrl.__init__(self, root, base)
        if base is None:
            raise TypeError("expected LabelUIControl, got " + str(type(base)))
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
        # type: (ToolDeltaScreen, ImageUIControl | None) -> None
        UBaseCtrl.__init__(self, root, base)
        if base is None:
            raise TypeError("expected ImageUIControl, got " + str(type(base)))
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
        # type: (ToolDeltaScreen, ButtonUIControl | None) -> None
        UBaseCtrl.__init__(self, root, base)
        if base is None:
            raise TypeError("expected ButtonUIControl, got " + str(type(base)))
        self.base = base

    def SetCallback(
        self,
        callback,  # type: Callable[[Any], Any]
    ):
        self.base.AddTouchEventParams({"isSwallow": True})
        self.base.SetButtonTouchUpCallback(callback)  # pyright: ignore[reportArgumentType]
        return self

    def SetOnRollOverCallback(
        self,
        callback,  # type: Callable[[dict], None]
    ):
        self.base.AddHoverEventParams()
        self.base.SetButtonHoverInCallback(callback)  # pyright: ignore[reportArgumentType]
        return self

    def SetOnRollOutCallback(
        self,
        callback,  # type: Callable[[dict], None]
    ):
        self.base.AddHoverEventParams()
        self.base.SetButtonHoverOutCallback(callback)  # pyright: ignore[reportArgumentType]
        return self


class UScrollView(UBaseCtrl):
    def __init__(self, root, base):
        # type: (ToolDeltaScreen, ScrollViewUIControl | None) -> None
        UBaseCtrl.__init__(self, root, base)
        if base is None:
            raise TypeError("expected ScrollViewUIControl, got " + str(type(base)))
        self.base = base

    def GetContent(self):
        return UBaseCtrl(self._root, self.base.GetScrollViewContentControl())


class UGrid(UBaseCtrl):
    def __init__(self, root, base):
        # type: (ToolDeltaScreen, GridUIControl | None) -> None
        UBaseCtrl.__init__(self, root, base)
        if base is None:
            raise TypeError("expected GridUIControl, got " + str(type(base)))
        self.path = self.base.GetPath()
        self.later_exec_cbs = []  # type: list[Callable[[], None]]
        self.base = base

    def GetGridDimension(self):
        # type: () -> tuple[int, int]
        return _get_gui().get_grid_dimension(
            self._root.base.GetScreenName(), self.getFullPath()
        )

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
            ExecLater(0, cb)
        else:
            self.SetGridDimension(xy)
            self.ExecuteAfterUpdate(cb)

    def ExecuteAfterUpdate(self, cb):
        # type: (Callable[[], None]) -> None
        self.later_exec_cbs.append(cb)
        grid_comp_size_changed_cbs[self.path] = self.onGridSizeChanged

    def onGridSizeChanged(self):
        try:
            for cb in self.later_exec_cbs:
                cb()
        finally:
            self.later_exec_cbs = []
        grid_comp_size_changed_cbs.pop(self.base.GetPath(), None)


class UComboBox(UBaseCtrl):
    def __init__(self, root, base):
        # type: (ToolDeltaScreen, NeteaseComboBoxUIControl | None) -> None
        UBaseCtrl.__init__(self, root, base)
        if base is None:
            raise TypeError("expected NeteaseComboBoxUIControl, got " + str(type(base)))
        self.base = base

    def AddOption(self, text, icon="", extra_data=None):
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
        # type: (ToolDeltaScreen, SliderUIControl | None) -> None
        UBaseCtrl.__init__(self, root, base)
        if base is None:
            raise TypeError("expected SliderUIControl, got " + str(type(base)))
        self.base = base

    def GetSliderValue(self):
        return self.base.GetSliderValue()

    def SetSliderValue(self, value):
        # type: (float) -> None
        self.base.SetSliderValue(value)


class UNeteasePaperDoll(UBaseCtrl):
    def __init__(self, root, base):
        # type: (ToolDeltaScreen, NeteasePaperDollUIControl | None) -> None
        UBaseCtrl.__init__(self, root, base)
        if base is None:
            raise TypeError(
                "expected NeteasePaperDollUIControl, got " + str(type(base))
            )
        self.base = base

    def RenderEntity(
        self,
        entity_id=None,  # type: str | None
        entity_identifier=None,  # type: str | None
        scale=1.0,  # type: float
        render_depth=-50,  # type: int
        init_rot_x=0,  # type: float
        init_rot_y=0,  # type: float
        init_rot_z=0,  # type: float
        molang_dict={},  # type: dict
        rotation_axis=(0, 0, 0),  # type: tuple[Literal[0, 1], Literal[0, 1], Literal[0, 1]]
    ):
        params = {
            "scale": scale,
            "render_depth": render_depth,
            "init_rot_x": init_rot_x,
            "init_rot_y": init_rot_y,
            "init_rot_z": init_rot_z,
            "molang_dict": molang_dict,
            "rotation_axis": rotation_axis,
        }  # type: dict
        if entity_id is not None:
            params["entity_id"] = entity_id
        if entity_identifier is not None:
            params["entity_identifier"] = entity_identifier
        return self.base.RenderEntity(params)

    def RenderBlockGeometryModel(
        self,
        block_geometry_model_name,  # type: str
        scale=1.0,  # type: float
        init_rot_y=0,  # type: float
        init_rot_x=0,  # type: float
        init_rot_z=0,  # type: float
        molang_dict=None,  # type: dict | None
        rotation_axis=(1, 0, 0),  # type: tuple[Literal[0, 1], Literal[0, 1], Literal[0, 1]]
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
        # type: (ToolDeltaScreen, TextEditBoxUIControl | None) -> None
        UBaseCtrl.__init__(self, root, base)
        if base is None:
            raise TypeError("expected TextEditBoxUIControl, got " + str(type(base)))
        self.base = base

    def GetText(self):
        return self.base.GetEditText()

    def SetText(self, text):
        # type: (str) -> None
        self.base.SetEditText(text)


class USwitch(UBaseCtrl):
    def __init__(self, root, base):
        # type: (ToolDeltaScreen, SwitchToggleUIControl | None) -> None
        UBaseCtrl.__init__(self, root, base)
        if base is None:
            raise TypeError("expected SwitchToggleUIControl, got " + str(type(base)))
        self.base = base

    def GetState(self, toggle_path="/this_toggle"):
        # type: (str) -> bool
        return self.base.GetToggleState(toggle_path)

    def SetState(self, state, toggle_path="/this_toggle"):
        # type: (bool, str) -> None
        self.base.SetToggleState(state, toggle_path)


def _get_gui():
    import traceback

    try:
        return getattr(traceback, "sys").modules["gui"]
    except AttributeError:

        class gui_missing:
            @staticmethod
            def get_grid_dimension(*_):
                return (0, 0)

        return gui_missing()


grid_comp_size_changed_cbs = dict()  # type: dict[str, Callable[[], None]]


@GridComponentSizeChangedClientEvent.Listen()
def onGridComponentSizeChanged(event):
    # type: (GridComponentSizeChangedClientEvent) -> None
    path = event.path
    if path.startswith("/main"):
        path = path[5:]
    cb = grid_comp_size_changed_cbs.pop(path, None)
    if cb:
        immediately = False
        if immediately:
            cb()
        else:
            ExecLater(
                0, cb
            )  # TODO: 不知道为什么 如果直接 cb() grid 会获取不到新 position。。


CONVERT_MAP = {
    UBaseCtrl: lambda x: x,
    UItemRenderer: lambda x: x.asItemRenderer(),
    ULabel: lambda x: x.asLabel(),
    UImage: lambda x: x.asImage(),
    UButton: lambda x: x.asButton(),
    UScrollView: lambda x: x.asScrollView(),
    UGrid: lambda x: x.asGrid(),
    UNeteasePaperDoll: lambda x: x.asNeteasePaperDoll(),
    USlider: lambda x: x.asSlider(),
}  # type: dict[type[UBaseCtrl], Callable[[BaseUIControl], BaseUIControl | None]]

__all__ = [
    "UBaseCtrl",
    "UItemRenderer",
    "ULabel",
    "UImage",
    "UButton",
    "USwitch",
    "UTextEditBoxUIControl",
    "UNeteasePaperDoll",
    "USlider",
    "UScrollView",
    "UGrid",
]
