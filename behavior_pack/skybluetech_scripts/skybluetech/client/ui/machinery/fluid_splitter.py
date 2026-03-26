# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.events.client import OnKeyPressInGame
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen, UBaseCtrl, Binder
from skybluetech_scripts.tooldelta.api.client import GetItemHoverName
from ....common.events.machinery.fluid_splitter import (
    FluidSplitterSettingsSetFluid,
    FluidSplitterSettingsSetLabel,
    FluidSplitterSettingsListUpdate,
    FluidSplitterSimpleAction,
)
from ....common.define.id_enum.fluids import all_fluids
from ....common.ui_sync.machinery.fluid_splitter import FluidSplitterUISync
from ..misc.transmitter_settings_ui import rand_rgb_by_index, get_opposite_color
from .define import MachinePanelUIProxy, MAIN_PATH
from .utils import InitFluidsDisplay

SETTINGS_VIEW_NODE = MAIN_PATH / "settings_view"
ADD_BTN_NODE = MAIN_PATH / "add_btn"
FLUID_DISP_NODE = MAIN_PATH / "fluid_display"


@RegistToolDeltaScreen("FluidSplitterUI.main", is_proxy=True)
class FluidSplitterUI(MachinePanelUIProxy):
    def OnCreate(self):
        dim, x, y, z = self.pos
        self.sync = FluidSplitterUISync.NewClient(dim, x, y, z)  # type: FluidSplitterUISync
        self.sync.SetUpdateCallback(self.WhenUpdated)
        self.settings_view = self.GetElement(SETTINGS_VIEW_NODE).asScrollView()
        self.settings_grid = self.settings_view.GetContent().asGrid()
        self.add_btn = (
            self.GetElement(ADD_BTN_NODE).asButton().SetCallback(self.onAddSetting)
        )
        self.label_selector_window = None
        self.fluid_selector_window = None
        self.fluid_selector_window_elements = [None] * 24  # type: list[UBaseCtrl | None]
        self.current_selected_fluid_id = None
        self.selected_setting_index = -1
        self.fluid_update_cb = InitFluidsDisplay(
            self.GetElement(FLUID_DISP_NODE),
            self.sync.fluids,
            0,
        )

    def OnDestroy(self):
        MachinePanelUIProxy.OnDestroy(self)
        self.closeLabelSelector()
        self.closeFluidSelector()

    def WhenUpdated(self):
        if not self.inited:
            return
        self.fluid_update_cb()

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

    def createLabelSelector(self, x, y):
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
            lambda _: self.closeLabelSelector()
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

    def closeLabelSelector(self):
        if self.label_selector_window is not None:
            self.label_selector_window.Remove()
            self.label_selector_window = None

    def createFluidSelector(self, x, y):
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
            lambda _: self.closeFluidSelector()
        )
        self.flushFluidSelector([])
        return window

    def closeFluidSelector(self):
        if self.fluid_selector_window is not None:
            self.fluid_selector_window.Remove()
            self.fluid_selector_window = None
            self.fluid_selector_window_elements = [None] * 24

    def flushFluidSelector(self, sections):
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
        dim, x, y, z = self.pos
        FluidSplitterSimpleAction(
            dim, x, y, z, FluidSplitterSimpleAction.ACTION_ADD_SETTING, 0
        ).send()

    @Binder.binding(Binder.BF_ButtonClick, "#FluidSplitterUI.label_editing")
    def onEditLabel(self, params):
        # print params
        if params["ButtonState"] != 0:
            return
        btn = self.GetElement(SETTINGS_VIEW_NODE / params["ButtonPath"])
        btn_x, btn_y = btn.GetRootPos()
        idx = params["#collection_index"]
        self.selected_setting_index = idx
        self.createLabelSelector(btn_x, btn_y)

    @Binder.binding(Binder.BF_ButtonClick, "#FluidSplitterUI.fluid_editing")
    def onEditFluid(self, params):
        # print params
        if params["ButtonState"] != 0:
            return
        btn = self.GetElement(SETTINGS_VIEW_NODE / params["ButtonPath"])
        btn_x, btn_y = btn.GetRootPos()
        idx = params["#collection_index"]
        self.selected_setting_index = idx
        self.createFluidSelector(btn_x, btn_y)

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
        self.closeLabelSelector()
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
            self.flushFluidSelector([])
            return
        searches = getFluidNamesForSearch()
        res = [searches[i] for i in fuzzySearch(text, list(searches))]
        self.flushFluidSelector(res)

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
        self.closeFluidSelector()

    @MachinePanelUIProxy.Listen(FluidSplitterSettingsListUpdate)
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


def getFluidNamesForSearch():
    if getFluidNamesForSearch.cache is None:
        SEARCHABLE_FLUIDS = {
            GetItemHoverName(fluid_id): fluid_id for fluid_id in all_fluids
        }
        SEARCHABLE_FLUIDS.update({fluid_id: fluid_id for fluid_id in all_fluids})
        getFluidNamesForSearch.cache = SEARCHABLE_FLUIDS
    return getFluidNamesForSearch.cache


getFluidNamesForSearch.cache = None
