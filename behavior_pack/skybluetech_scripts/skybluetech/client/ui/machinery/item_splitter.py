# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen, UBaseCtrl, Binder
from skybluetech_scripts.tooldelta.api.client import (
    GetItemHoverName,
    GetLocalPlayerHotbarAndInvItems,
)
from ....common.events.machinery.item_splitter import (
    ItemSplitterSettingsSetItem,
    ItemSplitterSettingsSetLabel,
    ItemSplitterSettingsListUpdate,
    ItemSplitterSimpleAction,
)
from ....common.ui_sync.machinery.item_splitter import ItemSplitterUISync
from ..misc.transmitter_settings_ui import rand_rgb_by_index, get_opposite_color
from .define import MachinePanelUIProxy, MAIN_PATH

SETTINGS_VIEW_NODE = MAIN_PATH / "settings_view"
ADD_BTN_NODE = MAIN_PATH / "add_btn"


@RegistToolDeltaScreen("ItemSplitterUI.main", is_proxy=True)
class ItemSplitterUI(MachinePanelUIProxy):
    def OnCreate(self):
        dim, x, y, z = self.pos
        self.sync = ItemSplitterUISync.NewClient(dim, x, y, z)  # type: ItemSplitterUISync
        self.sync.SetUpdateCallback(self.WhenUpdated)
        self.settings_view = self.GetElement(SETTINGS_VIEW_NODE).asScrollView()
        self.settings_grid = self.settings_view.GetContent().asGrid()
        self.add_btn = (
            self.GetElement(ADD_BTN_NODE).asButton().SetCallback(self.onAddSetting)
        )
        self.label_selector_window = None
        self.item_selector_window = None
        self.selected_setting_index = -1

    def OnDestroy(self):
        self.closeLabelSelector()
        self.closeItemSelector()

    def WhenUpdated(self):
        if not self.inited:
            return

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
            griditem["item_renderer"].asItemRenderer().SetUiItem(Item(fluid_id))

    def createLabelSelector(self, x, y):
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
            lambda _: self.closeLabelSelector()
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

    def closeLabelSelector(self):
        if self.label_selector_window is not None:
            self.label_selector_window.Remove()
            self.label_selector_window = None

    def createItemSelector(self, x, y):
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
            lambda _: self.closeItemSelector()
        )
        _i0 = 0
        items = GetLocalPlayerHotbarAndInvItems()
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

    def closeItemSelector(self):
        if self.item_selector_window is not None:
            self.item_selector_window.Remove()
            self.item_selector_window = None

    def onAddSetting(self, _):
        dim, x, y, z = self.pos
        ItemSplitterSimpleAction(
            dim, x, y, z, ItemSplitterSimpleAction.ACTION_ADD_SETTING, 0
        ).send()

    @Binder.binding(Binder.BF_ButtonClick, "#ItemSplitterUI.label_editing")
    def onEditLabel(self, params):
        # print params
        if params["ButtonState"] != 0:
            return
        btn = self.GetElement(SETTINGS_VIEW_NODE / params["ButtonPath"])
        btn_x, btn_y = btn.GetRootPos()
        idx = params["#collection_index"]
        self.selected_setting_index = idx
        self.createLabelSelector(btn_x, btn_y)

    @Binder.binding(Binder.BF_ButtonClick, "#ItemSplitterUI.item_editing")
    def onEditItem(self, params):
        # print params
        if params["ButtonState"] != 0:
            return
        btn = self.GetElement(SETTINGS_VIEW_NODE / params["ButtonPath"])
        btn_x, btn_y = btn.GetRootPos()
        idx = params["#collection_index"]
        self.selected_setting_index = idx
        self.createItemSelector(btn_x, btn_y)

    @Binder.binding(Binder.BF_ButtonClick, "#ItemSplitterUI.label_selected")
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
                "[Error] ItemSplitterUISync: onLabelSelected: selected_setting_index empty"
            )
            return
        self.closeLabelSelector()
        dim, x, y, z = self.pos
        ItemSplitterSettingsSetLabel(
            dim, x, y, z, self.selected_setting_index, idx
        ).send()

    @Binder.binding(Binder.BF_ButtonClick, "#ItemSplitterUI.item_selected")
    def onSelectItem(self, params):
        # print params
        if params["ButtonState"] != 0:
            return
        button_path = params["ButtonPath"][len("main/") :]
        idx = self.GetElement(button_path).GetPropertyBag().get("#index", 0)  # type: int
        if idx == -1:
            return
        if self.selected_setting_index == -1:
            print(
                "[Error] ItemSplitterUISync: onItemSelected: selected_setting_index empty"
            )
            return
        selected_item = GetLocalPlayerHotbarAndInvItems()[idx]
        if selected_item is None:
            return
        self.closeItemSelector()
        dim, x, y, z = self.pos
        ItemSplitterSettingsSetItem(
            dim, x, y, z, self.selected_setting_index, selected_item.id
        ).send()

    @Binder.binding(Binder.BF_ButtonClick, "#ItemSplitterUI.delete")
    def onDeleteSetting(self, params):
        # print params
        if params["ButtonState"] != 0:
            return
        idx = params["#collection_index"]
        dim, x, y, z = self.pos
        ItemSplitterSimpleAction(
            dim,
            x,
            y,
            z,
            ItemSplitterSimpleAction.ACTION_REMOVE_SETTING,
            idx,
        ).send()

    @MachinePanelUIProxy.DelayedListen(ItemSplitterSettingsListUpdate)
    def onListUpdated(self, event):
        # type: (ItemSplitterSettingsListUpdate) -> None
        cur = len(event.lis)
        self.settings_grid.SetDimensionAndCall(
            (1, cur), lambda: self.onGridUpdated(event.lis)
        )
