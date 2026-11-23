# coding=utf-8
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from mod.client.extraClientApi import GetLocalPlayerId, GetMinecraftEnum
from skybluetech_scripts.skybluetech.common.define.flags import DEACTIVE_FLAG_OUTPUT_FULL
from skybluetech_scripts.skybluetech.common.events.machinery.item_splitter import (
    ItemSplitterSettingsSetItem,
    ItemSplitterSettingsSetLabel,
    ItemSplitterSimpleAction,
)
from skybluetech_scripts.skybluetech.common.machinery_def.splitter_settings import (
    ITEM_SPLITTER_DEFAULT_ITEM,
    ITEM_SPLITTER_SETTINGS_LIMIT,
    K_RECORD_LABELS,
    K_SETTINGS_LIMIT,
    LoadSplitterSettings,
)
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui import Binder, RegistToolDeltaScreen, UBaseCtrl
from skybluetech_scripts.tooldelta.utils.nbt import GetValue, NBT2Py, ValueOf

from ..machinery_extra_pages import ItemPipeSettingsPageIndirectional
from ..misc.transmitter_settings_ui import get_opposite_color, rand_rgb_by_index
from .define_ex import MAIN_PATH, MachinePanelUIProxyEx

SETTINGS_VIEW_PATH = MAIN_PATH / "settings_view"
ADD_BTN_PATH = MAIN_PATH / "add_btn"
SETTINGS_COLLECTION = "item_splitter_settings_grid"
EMPTY_SETTING_ROW = ("", (1.0, 1.0, 1.0), 131072)


@RegistToolDeltaScreen("ItemSplitterUI.main", is_proxy=True)
class ItemSplitterUI(MachinePanelUIProxyEx):
    available_extra_pages = (ItemPipeSettingsPageIndirectional,)
    STATUS_TEXTS = {DEACTIVE_FLAG_OUTPUT_FULL: "送不出去（没有对应标签的出口或出口已满）"}
    STATUS_RINGS = {DEACTIVE_FLAG_OUTPUT_FULL: ("ring_in_container_slots",)}
    _setting_rows = ()  # type: tuple[tuple[str, tuple[float, float, float], int], ...]

    def OnCreate(self):
        self.label_selector_window = None
        self.item_selector_window = None
        self.selected_setting_index = -1
        self.settings = []
        self.settings_limit = 0

        settings_view = self.GetElement(SETTINGS_VIEW_PATH).asScrollView()
        self.settings_grid = settings_view.GetContent().asGrid()
        data = CF.CreateBlockInfo(LEVEL_ID).GetBlockEntityData(self.pos[1:])
        if data is not None:
            ex_data = ValueOf(data.get("exData")) or {}
            records = NBT2Py(GetValue(ex_data, K_RECORD_LABELS))
            self.settings = LoadSplitterSettings(records, ITEM_SPLITTER_DEFAULT_ITEM)
            self.settings_limit = (
                ValueOf(ex_data.get(K_SETTINGS_LIMIT)) or ITEM_SPLITTER_SETTINGS_LIMIT
            )
        self._refresh_setting_rows()
        self.GetElement(ADD_BTN_PATH).asButton().SetCallback(self.onAddSetting)

    def OnDestroy(self):
        MachinePanelUIProxyEx.OnDestroy(self)
        self.close_setting_selectors()

    def _refresh_setting_rows(self):
        item_comp = CF.CreateItem(LEVEL_ID)
        rows = []
        for label, item_id in self.settings:
            name = item_comp.GetItemHoverName(item_id) or item_id
            icon = item_comp.GetItemBasicInfo(item_id, 0, False) or {}
            rows.append(
                (name.replace("§f", ""), rand_rgb_by_index(label), icon.get("id_aux", 131072))
            )
        self._setting_rows = tuple(rows)

    def has_setting(self, index):
        return 0 <= index < len(self.settings)

    def _get_setting_row(self, index):
        rows = self._setting_rows
        return rows[index] if 0 <= index < len(rows) else EMPTY_SETTING_ROW

    @Binder.binding(Binder.BF_BindGridSize, "#ItemSplitterUI.settings_grid_size")
    def _get_settings_grid_size(self):
        return (1, len(self._setting_rows))

    @Binder.binding_collection(
        Binder.BF_BindString, SETTINGS_COLLECTION, "#ItemSplitterUI.setting_name"
    )
    def _get_setting_name(self, index):
        return self._get_setting_row(index)[0]

    @Binder.binding_collection(
        Binder.BF_BindColor, SETTINGS_COLLECTION, "#ItemSplitterUI.setting_color"
    )
    def _get_setting_color(self, index):
        return self._get_setting_row(index)[1]

    @Binder.binding_collection(
        Binder.BF_BindInt, SETTINGS_COLLECTION, "#ItemSplitterUI.setting_item_id_aux"
    )
    def _get_setting_item_id_aux(self, index):
        return self._get_setting_row(index)[2]

    def close_setting_selectors(self):
        self.close_label_selector()
        self.close_item_selector()

    def create_label_selector(self, x, y):
        # type: (float, float) -> UBaseCtrl
        if self.label_selector_window is not None:
            return self.label_selector_window
        window = self.AddElement(
            "ItemSplitterUI.label_selector", "label_selector_window"
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
            e = stack.AddElement(
                "ItemSplitterUI.label_index_selector", "selector%d" % i
            )
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

    def create_item_selector(self, x, y):
        # type: (float, float) -> UBaseCtrl
        if self.item_selector_window is not None:
            return self.item_selector_window
        window = self.AddElement("ItemSplitterUI.item_selector", "item_selector_window")
        window.SetLayer(90)
        stack = window["stack"]
        stack_sizex, _ = stack.GetSize()
        window.SetPos((x - stack_sizex / 2, y))
        self.item_selector_window = window
        self.item_selector_window["close_btn"].asButton().SetCallback(
            lambda _: self.close_item_selector()
        )
        _i0 = 0
        items = [
            Item.from_dict(it) if it is not None else None
            for it in CF.CreateItem(GetLocalPlayerId()).GetPlayerAllItems(
                GetMinecraftEnum().ItemPosType.INVENTORY, False
            )
        ]
        item_ids = set()  # type: set[str]
        for i in range(36):
            item = items[i]
            if item is None or item.id in item_ids:
                continue
            e = stack.AddElement(
                "ItemSplitterUI.item_index_selector", "selector%d" % _i0
            )
            xsize, ysize = e.GetSize()
            e.SetPos((_i0 * xsize % stack_sizex, _i0 // (stack_sizex // xsize) * ysize))
            e["item_renderer"].asItemRenderer().SetUiItem(item)
            e["btn"].SetPropertyBag({"#index": i})
            item_ids.add(item.id)
            _i0 += 1
        return window

    def close_item_selector(self):
        if self.item_selector_window is not None:
            self.item_selector_window.Remove()
            self.item_selector_window = None

    def onAddSetting(self, _):
        if len(self.settings) >= self.settings_limit:
            return
        self.settings.append((0, ITEM_SPLITTER_DEFAULT_ITEM))
        self._refresh_setting_rows()
        _, x, y, z = self.pos
        ItemSplitterSimpleAction(
            x, y, z, ItemSplitterSimpleAction.ACTION_ADD_SETTING, 0
        ).send()

    @Binder.binding(Binder.BF_ButtonClick, "#ItemSplitterUI.label_editing")
    def onEditLabel(self, params):
        idx = params.get("#collection_index", -1)
        if params["ButtonState"] != 0 or not self.has_setting(idx):
            return
        btn = self.GetElement(SETTINGS_VIEW_PATH / params["ButtonPath"])
        btn_x, btn_y = btn.GetRootPos()
        self.close_setting_selectors()
        self.selected_setting_index = idx
        self.create_label_selector(btn_x, btn_y)

    @Binder.binding(Binder.BF_ButtonClick, "#ItemSplitterUI.item_editing")
    def onEditItem(self, params):
        idx = params.get("#collection_index", -1)
        if params["ButtonState"] != 0 or not self.has_setting(idx):
            return
        btn = self.GetElement(SETTINGS_VIEW_PATH / params["ButtonPath"])
        btn_x, btn_y = btn.GetRootPos()
        self.close_setting_selectors()
        self.selected_setting_index = idx
        self.create_item_selector(btn_x, btn_y)

    @Binder.binding(Binder.BF_ButtonClick, "#ItemSplitterUI.label_selected")
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
        ItemSplitterSettingsSetLabel(x, y, z, index, label).send()

    @Binder.binding(Binder.BF_ButtonClick, "#ItemSplitterUI.item_selected")
    def onSelectItem(self, params):
        if params["ButtonState"] != 0:
            return
        button_path = params["ButtonPath"][len("main/") :]
        idx = self.GetElement(button_path).GetPropertyBag().get("#index", -1)  # type: int
        if idx == -1:
            return
        if self.selected_setting_index == -1:
            return
        selected_item = [
            Item.from_dict(it) if it is not None else None
            for it in CF.CreateItem(GetLocalPlayerId()).GetPlayerAllItems(
                GetMinecraftEnum().ItemPosType.INVENTORY, False
            )
        ][idx]
        if selected_item is None:
            return
        self.close_item_selector()
        self.set_setting_content(self.selected_setting_index, selected_item.id)

    def set_setting_content(self, index, item_id):
        if not self.has_setting(index) or not item_id or len(item_id) > 256:
            return False
        self.settings[index] = (self.settings[index][0], item_id)
        self._refresh_setting_rows()
        _, x, y, z = self.pos
        ItemSplitterSettingsSetItem(x, y, z, index, item_id).send()
        return True

    @Binder.binding(Binder.BF_ButtonClick, "#ItemSplitterUI.delete")
    def onDeleteSetting(self, params):
        index = params.get("#collection_index", -1)
        if params["ButtonState"] != 0 or not self.has_setting(index):
            return
        self.close_setting_selectors()
        self.selected_setting_index = -1
        self.settings.pop(index)
        self._refresh_setting_rows()
        _, x, y, z = self.pos
        ItemSplitterSimpleAction(
            x, y, z, ItemSplitterSimpleAction.ACTION_REMOVE_SETTING, index
        ).send()
