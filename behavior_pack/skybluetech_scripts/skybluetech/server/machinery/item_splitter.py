# coding=utf-8
from skybluetech_scripts.tooldelta.define.item import Item

from .basic.item_container import ItemContainer
from ...common.define import flags
from ...common.define.id_enum import Machinery, Upgraders
from ...common.events.machinery.item_splitter import (
    ItemSplitterSettingsSetItem,
    ItemSplitterSettingsSetLabel,
    ItemSplitterSimpleAction,
)
from ...common.machinery_def.splitter_settings import (
    ITEM_SPLITTER_DEFAULT_ITEM,
    ITEM_SPLITTER_SETTINGS_LIMIT,
    K_RECORD_LABELS,
    K_SETTINGS_LIMIT,
    LoadSplitterSettings,
    SaveSplitterSettings,
)
from ..transmitters.item_pipe.logic import (
    PushItemToGenericContainer,
)
from ..transmitters.item_pipe.logic import (
    logic_module as item_pipe_logic,
)
from .basic import GUIControl, OperationListener, UpgradeControl
from .core import RegisterMachine


@RegisterMachine
class ItemSplitter(OperationListener, UpgradeControl, GUIControl):
    block_name = Machinery.ITEM_SPLITTER
    item_input_slots = (0, 1, 2)
    upgrade_slot_start = 3
    allow_upgraders = frozenset({
        Upgraders.GENERIC_SPLIT,
    })

    def __init__(self, dim, x, y, z, block_entity_data):
        super(ItemSplitter, self).__init__(dim, x, y, z, block_entity_data)
        self._cached_recorded_settings = None
        self._sending_items = True
        self._ticking_t = 0
        self.handler.SubscribeOnTicking(self._item_splitter_on_ticking)
        self.handler.SubscribeOnSlotUpdate(self._item_splitter_on_slot_update)

    def _item_splitter_on_ticking(self):
        if self._sending_items and self._ticking_t % 5 == 0:
            has_item = False
            moved = False
            for slot in self.item_input_slots:
                item = self.GetSlotItem(slot)
                if item is not None:
                    has_item = True
                else:
                    continue
                it = self.try_post_item_by_label(item)
                if it is not None and it.id == item.id and it.count == item.count:
                    continue
                moved = True
                self.SetSlotItem(slot, it)
            # 状态灯: 空 = 缺少输入; 有物品但这一轮一件都没送出去 = 输出受阻
            self.UpdateDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT, not has_item)
            self.UpdateDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL, has_item and not moved)
            if not has_item:
                self._sending_items = False
        self._ticking_t += 1

    def IsValidInput(self, slot, item):
        # type: (int, Item) -> bool
        results = (
            ItemContainer.IsValidInput(self, slot, item),
            UpgradeControl.IsValidInput(self, slot, item),
            self._item_splitter_is_valid_input(slot, item),
        )
        return all(results)

    def _item_splitter_is_valid_input(self, slot, item):
        # type: (int, Item) -> bool
        if self.InUpgradeSlot(slot):
            return UpgradeControl.IsValidInput(self, slot, item)
        return True

    def _item_splitter_on_slot_update(self, slot):
        if not self.InUpgradeSlot(slot):
            self._sending_items = True
        else:
            return

    def try_post_item_by_label(self, item):
        # type: (Item) -> Item | None
        matched_label = self.get_label_by_item(item.id)
        networks = (
            item_pipe_logic
            .GetContainerNode(self.dim, self.x, self.y, self.z, enable_cache=True)
            .get_outputs()
            .values()
        )
        for network in networks:
            for ap in network.get_input_access_points():
                ap_label = ap.get_label()
                if ap_label == matched_label:
                    ret_item = PushItemToGenericContainer(ap, item)
                    if ret_item is None:
                        return None
                    else:
                        item = ret_item
        return item

    def get_label_by_item(self, item_id):
        # type: (str) -> int
        for label, _item_id in self.record_settings:
            if item_id == _item_id:
                return label
        return 0 if self.HasUpgrader(Upgraders.GENERIC_SPLIT) else -1

    def on_add_setting(self):
        if len(self.record_settings) >= self.settings_limit:
            return
        self.record_settings.append((0, ITEM_SPLITTER_DEFAULT_ITEM))
        self.save_settings()

    def on_delete_setting(self, index):
        # type: (int) -> None
        if not 0 <= index < len(self.record_settings):
            return
        self.record_settings.pop(index)
        self.save_settings()

    def on_set_item(self, index, item):
        # type: (int, str) -> None
        if not 0 <= index < len(self.record_settings):
            return
        self.record_settings[index] = (self.record_settings[index][0], item)
        self.save_settings()

    def on_set_label(self, index, label):
        # type: (int, int) -> None
        if not 0 <= index < len(self.record_settings):
            return
        self.record_settings[index] = (label, self.record_settings[index][1])
        self.save_settings()

    @property
    def settings_limit(self):
        # type: () -> int
        return self.bdata[K_SETTINGS_LIMIT] or ITEM_SPLITTER_SETTINGS_LIMIT

    @settings_limit.setter
    def settings_limit(self, value):
        # type: (int) -> None
        self.bdata[K_SETTINGS_LIMIT] = value

    @property
    def record_settings(self):
        if self._cached_recorded_settings is None:
            self._cached_recorded_settings = LoadSplitterSettings(
                self.bdata[K_RECORD_LABELS], ITEM_SPLITTER_DEFAULT_ITEM
            )
        return self._cached_recorded_settings

    @record_settings.setter
    def record_settings(self, value):
        # type: (list[tuple[int, str]]) -> None
        self._cached_recorded_settings = value
        self.save_settings()

    def save_settings(self):
        self.bdata[K_RECORD_LABELS] = SaveSplitterSettings(self.record_settings)


@ItemSplitter.ForOperation(ItemSplitterSimpleAction)
def onSimpleAction(event, machine):
    # type: (ItemSplitterSimpleAction, ItemSplitter) -> None
    if event.action == event.ACTION_ADD_SETTING:
        machine.on_add_setting()
    elif event.action == event.ACTION_REMOVE_SETTING and isinstance(event.extra, int):
        machine.on_delete_setting(event.extra)


@ItemSplitter.ForOperation(ItemSplitterSettingsSetLabel)
def onSetLabel(event, machine):
    # type: (ItemSplitterSettingsSetLabel, ItemSplitter) -> None
    if not isinstance(event.label, int) or not isinstance(event.setting_index, int):
        return
    machine.on_set_label(event.setting_index, event.label)


@ItemSplitter.ForOperation(ItemSplitterSettingsSetItem)
def onSetItem(event, machine):
    # type: (ItemSplitterSettingsSetItem, ItemSplitter) -> None
    if (
        not isinstance(event.setting_index, int)
        or not isinstance(event.item_id, str)
        or len(event.item_id) > 256
    ):
        return
    machine.on_set_item(event.setting_index, event.item_id)
