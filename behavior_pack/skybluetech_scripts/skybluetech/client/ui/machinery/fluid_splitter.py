# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.id_enum.fluids import Fluids
from skybluetech_scripts.skybluetech.common.events.machinery.fluid_splitter import (
    FluidSplitterSettingsListUpdate,
    FluidSplitterSettingsSetFluid,
    FluidSplitterSettingsSetLabel,
    FluidSplitterSimpleAction,
)
from skybluetech_scripts.skybluetech.common.machinery_def.basic import FluidSlotClient
from skybluetech_scripts.skybluetech.common.machinery_def.fluid_splitter import (
    MAX_FLUID_VOLUME,
)
from skybluetech_scripts.tooldelta.api.client import (
    GetBlockEntityData,
    GetItemHoverName,
)
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.events.client import OnKeyPressInGame
from skybluetech_scripts.tooldelta.ui import Binder, RegistToolDeltaScreen, UBaseCtrl

from ..machinery_extra_pages import PipeSettingsPageIndirectional
from ..misc.transmitter_settings_ui import get_opposite_color, rand_rgb_by_index
from .define_ex import MAIN_PATH, MachinePanelUIProxyEx
from .utils import FluidDisplayer

SETTINGS_VIEW_PATH = MAIN_PATH / "settings_view"
ADD_BTN_PATH = MAIN_PATH / "add_btn"
FLUID_DISP_PATH = MAIN_PATH / "fluid_display"


@RegistToolDeltaScreen("FluidSplitterUI.main", is_proxy=True)
class FluidSplitterUI(MachinePanelUIProxyEx):
    available_extra_pages = (PipeSettingsPageIndirectional,)

    def OnCreate(self):
        self.settings_view = self.GetElement(SETTINGS_VIEW_PATH).asScrollView()
        self.settings_grid = self.settings_view.GetContent().asGrid()
        self.add_btn = (
            self.GetElement(ADD_BTN_PATH).asButton().SetCallback(self.onAddSetting)
        )
        self.label_selector_window = None
        self.fluid_selector_window = None
        self.fluid_selector_window_elements = [None] * 24  # type: list[UBaseCtrl | None]
        self.current_selected_fluid_id = None
        self.selected_setting_index = -1
        self.fluid_displayer = FluidDisplayer(self.GetElement(FLUID_DISP_PATH))

    def OnDestroy(self):
        MachinePanelUIProxyEx.OnDestroy(self)
        self.close_label_selector()
        self.close_fluid_selector()

    def OnTicking(self):
        data = GetBlockEntityData(*self.pos[1:])
        if data is None:
            return
        data = data["exData"]
        fluid = FluidSlotClient(data)
        self.fluid_displayer.update(fluid.fluid_id, fluid.volume, MAX_FLUID_VOLUME)

    def onGridUpdated(self, lis):
        # type: (list[tuple[int, str]]) -> None
        items_count = self.settings_grid.GetGridDimension()[1]
        for i in range(items_count):
            label, fluid_id = lis[i]
            griditem = self.settings_grid.GetGridItem(0, i)
            griditem["label"].asLabel().SetText(
                GetItemHoverName(fluid_id).replace("§f", "")
            )
            griditem["color_img"].asImage().SetSpriteColor(rand_rgb_by_index(label))
            griditem["item_renderer"].asItemRenderer().SetUiItem(
                Item(fluid_id + "_bucket")
            )

    def create_label_selector(self, x, y):  
        # type: (float, float) -> UBaseCtrl
        self.selected_setting_index
        if self.label_selector_window is not None:
            return self.label_selector_window
        window = self.AddElement(
            "FluidSplitterUI.label_selector_window", "label_selector_window"
        )
        window.SetLayer(80)
        stack = window["stack"]
        stack_sizex, _ = stack.GetSize()
        window.SetPos((x, y))
        self.label_selector_window = window
        self.label_selector_window["close_btn"].asButton().SetCallback(
            lambda _: self.close_label_selector()
        )
        for i in range(24):
            e = stack.AddElement("FluidSplitterUI.index_selector", "selector%d" % i)
            xsize, ysize = e.GetSize()
            e.SetPos((i * xsize % stack_sizex, i // (stack_sizex // xsize) * ysize))
            r, g, b = rand_rgb_by_index(i)
            e["color_img"].asImage().SetSpriteColor((r, g, b))
            e["index_num"].asLabel().SetColor(get_opposite_color(r, g, b))
            e["index_num"].asLabel().SetText("§l%d" % i)
            e["btn"].SetPropertyBag({"#index": i})
            self.fluid_selector_window_elements.append(e)
        return window

    def close_label_selector(self):
        if self.label_selector_window is not None:
            self.label_selector_window.Remove()
            self.label_selector_window = None

    def create_fluid_selector(self, x, y):
        # type: (float, float) -> UBaseCtrl
        self.selected_setting_index
        if self.fluid_selector_window is not None:
            return self.fluid_selector_window
        window = self.AddElement(
            "FluidSplitterUI.fluid_selector_window", "fluid_selector_window"
        )
        window.SetLayer(80)
        window.SetPos((x - 80, y))
        window["title"].asLabel().SetText("选择流体")
        self.fluid_selector_window = window
        self.fluid_selector_window["close_btn"].asButton().SetCallback(
            lambda _: self.close_fluid_selector()
        )
        self.flush_fluid_selector([])
        return window

    def close_fluid_selector(self):
        if self.fluid_selector_window is not None:
            self.fluid_selector_window.Remove()
            self.fluid_selector_window = None
            self.fluid_selector_window_elements = [None] * 24

    def flush_fluid_selector(self, sections):
        # type: (list[str]) -> None
        if self.fluid_selector_window is None:
            return
        for e in self.fluid_selector_window_elements:
            if e is not None:
                e.SetVisible(False, True)
        stack = self.fluid_selector_window["stack"]
        stack_sizex, _ = stack.GetSize()
        for i, section in enumerate(sections[:24]):
            e = self.fluid_selector_window_elements[i]
            if e is None:
                e = stack.AddElement("FluidSplitterUI.fluid_selector", "selector%d" % i)
                self.fluid_selector_window_elements[i] = e
            else:
                e.SetVisible(True, True)
            xsize, ysize = e.GetSize()
            e.SetPos((i * xsize % stack_sizex, i // (stack_sizex // xsize) * ysize))
            e["item_renderer"].asItemRenderer().SetUiItem(Item(section + "_bucket"))
            e["btn"].SetPropertyBag({"#fluid_id": section})

    def onAddSetting(self, _):
        _, x, y, z = self.pos
        FluidSplitterSimpleAction(
            x, y, z, FluidSplitterSimpleAction.ACTION_ADD_SETTING, 0
        ).send()

    @Binder.binding(Binder.BF_ButtonClick, "#FluidSplitterUI.label_editing")
    def onEditLabel(self, params):
        # print params
        if params["ButtonState"] != 0:
            return
        btn = self.GetElement(SETTINGS_VIEW_PATH / params["ButtonPath"])
        btn_x, btn_y = btn.GetRootPos()
        idx = params["#collection_index"]
        self.selected_setting_index = idx
        self.create_label_selector(btn_x, btn_y)

    @Binder.binding(Binder.BF_ButtonClick, "#FluidSplitterUI.fluid_editing")
    def onEditFluid(self, params):
        # print params
        if params["ButtonState"] != 0:
            return
        btn = self.GetElement(SETTINGS_VIEW_PATH / params["ButtonPath"])
        btn_x, btn_y = btn.GetRootPos()
        idx = params["#collection_index"]
        self.selected_setting_index = idx
        self.create_fluid_selector(btn_x, btn_y)

    @Binder.binding(Binder.BF_ButtonClick, "#FluidSplitterUI.label_selected")
    def onSelectLabel(self, params):
        # print params
        if params["ButtonState"] != 0:
            return
        button_path = params["ButtonPath"][len("main/") :]
        idx = self.GetElement(button_path).GetPropertyBag().get("#index", -1)
        if idx == -1:
            return
        if self.selected_setting_index == -1:
            print(
                "[Error] FluidSplitterUISync: onLabelSelected: selected_setting_index empty"
            )
            return
        self.close_label_selector()
        dim, x, y, z = self.pos
        FluidSplitterSettingsSetLabel(
            dim, x, y, z, self.selected_setting_index, idx
        ).send()

    @Binder.binding(Binder.BF_ButtonClick, "#FluidSplitterUI.fluid_selected")
    def onSelectFluid(self, params):
        # print params
        if params["ButtonState"] != 0:
            return
        button_path = params["ButtonPath"][len("main/") :]
        fluid_id = str(
            self.GetElement(button_path).GetPropertyBag().get("#fluid_id", "")
        )
        if fluid_id == "":
            return
        if self.selected_setting_index == -1:
            print(
                "[Error] FluidSplitterUISync: onFluidSelected: selected_setting_index empty"
            )
            return
        if self.fluid_selector_window is not None:
            self.fluid_selector_window["title"].asLabel().SetText(
                "选中流体： " + GetItemHoverName(fluid_id).replace("§f", "")
            )
            self.current_selected_fluid_id = fluid_id

    @Binder.binding(Binder.BF_ButtonClick, "#FluidSplitterUI.delete")
    def onDeleteSetting(self, params):
        # print params
        if params["ButtonState"] != 0:
            return
        idx = params["#collection_index"]
        dim, x, y, z = self.pos
        FluidSplitterSimpleAction(
            dim,
            x,
            y,
            z,
            FluidSplitterSimpleAction.ACTION_REMOVE_SETTING,
            idx,
        ).send()

    @Binder.binding(Binder.BF_EditChanged, "#FluidSplitterUI.search_fluid")
    def onSearchFluid(self, params):
        text = params["Text"]  # type: str
        if not text.replace(":", "").strip():
            self.flush_fluid_selector([])
            return
        searches = _get_all_fluid_names()
        res = [searches[i] for i in fuzzySearch(text, list(searches))]
        self.flush_fluid_selector(res)

    @Binder.binding(Binder.BF_ButtonClick, "#FluidSplitterUI.fluid_selected_confirm")
    def onConfirmFluid(self, params):
        dim, x, y, z = self.pos
        fluid_id = self.current_selected_fluid_id
        if fluid_id is None:
            return
        self.current_selected_fluid_id = None
        FluidSplitterSettingsSetFluid(
            dim, x, y, z, self.selected_setting_index, fluid_id
        ).send()
        self.close_fluid_selector()

    @MachinePanelUIProxyEx.Listen(FluidSplitterSettingsListUpdate)
    def onListUpdated(self, event):
        # type: (FluidSplitterSettingsListUpdate) -> None
        cur = len(event.lis)
        self.settings_grid.SetDimensionAndCall(
            (1, cur), lambda: self.onGridUpdated(event.lis)
        )


def fuzzySearch(text, sections):
    # type: (str, list[str]) -> list[str]
    keywords = text.split()
    return [
        section
        for section in sections
        if all(keyword in section for keyword in keywords)
    ]


def _get_all_fluid_names():
    if _get_all_fluid_names.cache is None:
        SEARCHABLE_FLUIDS = {
            GetItemHoverName(fluid_id).replace("§f", ""): fluid_id for fluid_id in Fluids.all_sub()
        }
        SEARCHABLE_FLUIDS.update({fluid_id: fluid_id for fluid_id in Fluids.all_sub()})
        _get_all_fluid_names.cache = SEARCHABLE_FLUIDS
    return _get_all_fluid_names.cache


_get_all_fluid_names.cache = None
