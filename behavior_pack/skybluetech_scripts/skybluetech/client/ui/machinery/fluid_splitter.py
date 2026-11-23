# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.flags import (
    DEACTIVE_FLAG_OUTPUT_FULL,
)
from skybluetech_scripts.skybluetech.common.define.id_enum.fluids import Fluids
from skybluetech_scripts.skybluetech.common.events.machinery.fluid_splitter import (
    FluidSplitterSettingsSetFluid,
    FluidSplitterSettingsSetLabel,
    FluidSplitterSimpleAction,
)
from skybluetech_scripts.skybluetech.common.machinery_def.basic import FluidSlotClient
from skybluetech_scripts.skybluetech.common.machinery_def.fluid_splitter import (
    MAX_FLUID_VOLUME,
)
from skybluetech_scripts.skybluetech.common.machinery_def.splitter_settings import (
    FLUID_SPLITTER_DEFAULT_FLUID,
    FLUID_SPLITTER_SETTINGS_LIMIT,
    K_RECORD_LABELS,
    K_SETTINGS_LIMIT,
    LoadSplitterSettings,
)
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui import Binder, RegistToolDeltaScreen, UBaseCtrl
from skybluetech_scripts.tooldelta.utils.nbt import GetValue, NBT2Py, ValueOf

from ..machinery_extra_pages import FluidPipeSettingsPageIndirectional
from ..misc.transmitter_settings_ui import get_opposite_color, rand_rgb_by_index
from .define_ex import MAIN_PATH, MachinePanelUIProxyEx
from .utils import FluidDisplayer

SETTINGS_VIEW_PATH = MAIN_PATH / "settings_view"
ADD_BTN_PATH = MAIN_PATH / "add_btn"
FLUID_DISP_PATH = MAIN_PATH / "fluid_display"
SETTINGS_COLLECTION = "fluid_splitter_settings_grid"
EMPTY_SETTING_ROW = ("", (1.0, 1.0, 1.0), 131072)


@RegistToolDeltaScreen("FluidSplitterUI.main", is_proxy=True)
class FluidSplitterUI(MachinePanelUIProxyEx):
    available_extra_pages = (FluidPipeSettingsPageIndirectional,)
    STATUS_TEXTS = {DEACTIVE_FLAG_OUTPUT_FULL: "送不出去（没有对应标签的出口或出口已满）"}
    STATUS_RINGS = {DEACTIVE_FLAG_OUTPUT_FULL: ("ring_tin_fluid_display",)}
    _setting_rows = ()  # type: tuple[tuple[str, tuple[float, float, float], int], ...]

    def OnCreate(self):
        self.label_selector_window = None
        self.fluid_selector_window = None
        self.fluid_selector_window_elements = [None] * 24  # type: list[UBaseCtrl | None]
        self.current_selected_fluid_id = None
        self.fluid_displayer = FluidDisplayer(self.GetElement(FLUID_DISP_PATH))
        self.selected_setting_index = -1
        self.settings = []
        self.settings_limit = 0

        data = CF.CreateBlockInfo(LEVEL_ID).GetBlockEntityData(self.pos[1:])
        if data is not None:
            ex_data = ValueOf(data.get("exData")) or {}
            records = NBT2Py(GetValue(ex_data, K_RECORD_LABELS))
            self.settings = LoadSplitterSettings(records, FLUID_SPLITTER_DEFAULT_FLUID)
            self.settings_limit = (
                ValueOf(ex_data.get(K_SETTINGS_LIMIT)) or FLUID_SPLITTER_SETTINGS_LIMIT
            )
        self._refresh_setting_rows()
        self.GetElement(ADD_BTN_PATH).asButton().SetCallback(self.onAddSetting)

    def OnDestroy(self):
        MachinePanelUIProxyEx.OnDestroy(self)
        self.close_setting_selectors()

    def _refresh_setting_rows(self):
        item_comp = CF.CreateItem(LEVEL_ID)
        rows = []
        for label, fluid_id in self.settings:
            name = item_comp.GetItemHoverName(fluid_id) or fluid_id
            icon = item_comp.GetItemBasicInfo(fluid_id + "_bucket", 0, False) or {}
            rows.append(
                (name.replace("§f", ""), rand_rgb_by_index(label), icon.get("id_aux", 131072))
            )
        self._setting_rows = tuple(rows)

    def has_setting(self, index):
        return 0 <= index < len(self.settings)

    def _get_setting_row(self, index):
        rows = self._setting_rows
        return rows[index] if 0 <= index < len(rows) else EMPTY_SETTING_ROW

    @Binder.binding(Binder.BF_BindGridSize, "#FluidSplitterUI.settings_grid_size")
    def _get_settings_grid_size(self):
        return (1, len(self._setting_rows))

    @Binder.binding_collection(
        Binder.BF_BindString, SETTINGS_COLLECTION, "#FluidSplitterUI.setting_name"
    )
    def _get_setting_name(self, index):
        return self._get_setting_row(index)[0]

    @Binder.binding_collection(
        Binder.BF_BindColor, SETTINGS_COLLECTION, "#FluidSplitterUI.setting_color"
    )
    def _get_setting_color(self, index):
        return self._get_setting_row(index)[1]

    @Binder.binding_collection(
        Binder.BF_BindInt, SETTINGS_COLLECTION, "#FluidSplitterUI.setting_item_id_aux"
    )
    def _get_setting_item_id_aux(self, index):
        return self._get_setting_row(index)[2]

    def close_setting_selectors(self):
        self.close_label_selector()
        self.close_fluid_selector()

    def OnTicking(self):
        data = CF.CreateBlockInfo(LEVEL_ID).GetBlockEntityData(self.pos[1:])
        if data is None:
            return
        data = data["exData"]
        fluid = FluidSlotClient(data)
        self.fluid_displayer.update(fluid.fluid_id, fluid.volume, MAX_FLUID_VOLUME)

    def create_label_selector(self, x, y):
        # type: (float, float) -> UBaseCtrl
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
        return window

    def close_label_selector(self):
        if self.label_selector_window is not None:
            self.label_selector_window.Remove()
            self.label_selector_window = None

    def create_fluid_selector(self, x, y):
        # type: (float, float) -> UBaseCtrl
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
        self.current_selected_fluid_id = None
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
        if len(self.settings) >= self.settings_limit:
            return
        self.settings.append((0, FLUID_SPLITTER_DEFAULT_FLUID))
        self._refresh_setting_rows()
        _, x, y, z = self.pos
        FluidSplitterSimpleAction(
            x, y, z, FluidSplitterSimpleAction.ACTION_ADD_SETTING, 0
        ).send()

    @Binder.binding(Binder.BF_ButtonClick, "#FluidSplitterUI.label_editing")
    def onEditLabel(self, params):
        idx = params.get("#collection_index", -1)
        if params["ButtonState"] != 0 or not self.has_setting(idx):
            return
        btn = self.GetElement(SETTINGS_VIEW_PATH / params["ButtonPath"])
        btn_x, btn_y = btn.GetRootPos()
        self.close_setting_selectors()
        self.selected_setting_index = idx
        self.create_label_selector(btn_x, btn_y)

    @Binder.binding(Binder.BF_ButtonClick, "#FluidSplitterUI.fluid_editing")
    def onEditFluid(self, params):
        idx = params.get("#collection_index", -1)
        if params["ButtonState"] != 0 or not self.has_setting(idx):
            return
        btn = self.GetElement(SETTINGS_VIEW_PATH / params["ButtonPath"])
        btn_x, btn_y = btn.GetRootPos()
        self.close_setting_selectors()
        self.selected_setting_index = idx
        self.create_fluid_selector(btn_x, btn_y)

    @Binder.binding(Binder.BF_ButtonClick, "#FluidSplitterUI.label_selected")
    def onSelectLabel(self, params):
        if params["ButtonState"] != 0:
            return
        button_path = params["ButtonPath"][len("main/") :]
        label = self.GetElement(button_path).GetPropertyBag().get("#index", -1)
        index = self.selected_setting_index
        if label == -1 or not self.has_setting(index):
            return
        self.close_label_selector()
        self.settings[index] = (label, self.settings[index][1])
        self._refresh_setting_rows()
        _, x, y, z = self.pos
        FluidSplitterSettingsSetLabel(x, y, z, index, label).send()

    @Binder.binding(Binder.BF_ButtonClick, "#FluidSplitterUI.fluid_selected")
    def onSelectFluid(self, params):
        if params["ButtonState"] != 0:
            return
        button_path = params["ButtonPath"][len("main/") :]
        fluid_id = str(
            self.GetElement(button_path).GetPropertyBag().get("#fluid_id", "")
        )
        if fluid_id == "":
            return
        if self.fluid_selector_window is not None:
            self.fluid_selector_window["title"].asLabel().SetText(
                "选中流体： " + CF.CreateItem(LEVEL_ID).GetItemHoverName(fluid_id).replace("§f", "")
            )
            self.current_selected_fluid_id = fluid_id

    @Binder.binding(Binder.BF_ButtonClick, "#FluidSplitterUI.delete")
    def onDeleteSetting(self, params):
        index = params.get("#collection_index", -1)
        if params["ButtonState"] != 0 or not self.has_setting(index):
            return
        self.close_setting_selectors()
        self.selected_setting_index = -1
        self.settings.pop(index)
        self._refresh_setting_rows()
        _, x, y, z = self.pos
        FluidSplitterSimpleAction(
            x, y, z, FluidSplitterSimpleAction.ACTION_REMOVE_SETTING, index
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
        if params["ButtonState"] != 0:
            return
        fluid_id = self.current_selected_fluid_id
        index = self.selected_setting_index
        if not self.has_setting(index) or not fluid_id or len(fluid_id) > 256:
            return
        self.settings[index] = (self.settings[index][0], fluid_id)
        self._refresh_setting_rows()
        _, x, y, z = self.pos
        FluidSplitterSettingsSetFluid(x, y, z, index, fluid_id).send()
        self.close_fluid_selector()


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
            CF.CreateItem(LEVEL_ID).GetItemHoverName(fluid_id).replace("§f", ""): fluid_id
            for fluid_id in Fluids.all_sub()
        }
        SEARCHABLE_FLUIDS.update({fluid_id: fluid_id for fluid_id in Fluids.all_sub()})
        _get_all_fluid_names.cache = SEARCHABLE_FLUIDS
    return _get_all_fluid_names.cache


_get_all_fluid_names.cache = None
