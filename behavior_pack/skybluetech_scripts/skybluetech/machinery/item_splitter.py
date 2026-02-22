# coding=utf-8
from mod.server.blockEntityData import BlockEntityData
from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.events.server import ServerBlockUseEvent
from skybluetech_scripts.tooldelta.api.common import ExecLater
from ..define.events.machinery.item_splitter import (
    ItemSplitterSettingsListUpdate,
    ItemSplitterSettingsSetItem,
    ItemSplitterSettingsSetLabel,
    ItemSplitterSimpleAction,
)
from ..define.id_enum.machinery import ITEM_SPLITTER as MACHINE_ID
from ..transmitters.cable.logic import (
    logic_module as cable_logic,
    PushItemToGenericContainer,
)
from ..ui_sync.machinery.item_splitter import ItemSplitterUISync
from ..utils.action_commit import SafeGetMachine
from .basic import GUIControl, UpgradeControl, RegisterMachine

K_RECORD_LABELS = "record_settings"
K_SETTINGS_LIMIT = "settings_limit"

DEFAULT_SETTINGS_LIMIT = 3


@RegisterMachine
class ItemSplitter(GUIControl, UpgradeControl):
    block_name = MACHINE_ID
    input_slots = (0, 1, 2)
    upgrade_slot_start = 3
    allow_upgrader_tags = {"skybluetech:upgraders/generic_split"}

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        UpgradeControl.__init__(self, dim, x, y, z, block_entity_data)
        self.sync = ItemSplitterUISync.NewServer(self).Activate()
        self._cached_recorded_settings = None

    def IsValidInput(self, slot, item):
        # type: (int, Item) -> bool
        if self.InUpgradeSlot(slot):
            return UpgradeControl.IsValidInput(self, slot, item)
        return True

    def OnSlotUpdate(self, slot):
        if slot in self.input_slots:
            item = self.GetSlotItem(slot)
            if item is None:
                return
            res = self.tryPostItemByLabel(item)
            self.SetSlotItem(slot, res)
        elif self.InUpgradeSlot(slot):
            UpgradeControl.OnSlotUpdate(self, slot)

    def tryPostItemByLabel(self, item):
        # type: (Item) -> Item | None
        matched_label = self.getLabelByItem(item.id)
        networks = (
            i
            for i in cable_logic.GetContainerNode(
                self.dim, self.x, self.y, self.z, enable_cache=True
            ).outputs.values()
            if i is not None
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

    def getLabelByItem(self, item_id):
        # type: (str) -> int
        for label, _item_id in self.record_settings:
            if item_id == _item_id:
                return label
        return 0 if self.HasUpgrader("skybluetech:upgrader_generic_split") else -1

    def OnClick(self, event):
        # type: (ServerBlockUseEvent) -> None
        GUIControl.OnClick(self, event)
        ExecLater(
            0.1,
            lambda: ItemSplitterSettingsListUpdate(self.record_settings).send(
                event.playerId
            ),
        )

    def OnUnload(self):
        # type: () -> None
        UpgradeControl.OnUnload(self)
        GUIControl.OnUnload(self)

    def onAddSetting(self, player_id):
        # type: (str) -> None
        if len(self.record_settings) >= self.settings_limit:
            return
        self.record_settings.append((0, "minecraft:apple"))
        self.save_settings()
        ItemSplitterSettingsListUpdate(self.record_settings).send(player_id)

    def onDeleteSetting(self, player_id, index):
        # type: (str, int) -> None
        if index >= len(self.record_settings):
            return
        self.record_settings.pop(index)
        self.save_settings()
        ItemSplitterSettingsListUpdate(self.record_settings).send(player_id)

    def onSetItem(self, player_id, index, item):
        # type: (str, int, str) -> None
        if index >= len(self.record_settings):
            return
        self.record_settings[index] = (self.record_settings[index][0], item)
        self.save_settings()
        ItemSplitterSettingsListUpdate(self.record_settings).send(player_id)

    def onSetLabel(self, player_id, index, label):
        # type: (str, int, int) -> None
        if index >= len(self.record_settings):
            return
        self.record_settings[index] = (label, self.record_settings[index][1])
        self.save_settings()
        ItemSplitterSettingsListUpdate(self.record_settings).send(player_id)

    @property
    def settings_limit(self):
        # type: () -> int
        return self.bdata[K_SETTINGS_LIMIT] or DEFAULT_SETTINGS_LIMIT

    @settings_limit.setter
    def settings_limit(self, value):
        # type: (int) -> None
        self.bdata[K_SETTINGS_LIMIT] = value

    @property
    def record_settings(self):
        if self._cached_recorded_settings is None:
            record_settings = self.bdata[K_RECORD_LABELS] or ["0-minecraft:water"]
            self._cached_recorded_settings = [
                (int(i.split("-")[0]), str(i.split("-")[1])) for i in record_settings
            ]
        return self._cached_recorded_settings

    @record_settings.setter
    def record_settings(self, value):
        # type: (list[tuple[int, str]]) -> None
        self._cached_recorded_settings = value
        self.bdata[K_RECORD_LABELS] = ["%d-%s" % (a, b) for a, b in value]

    def save_settings(self):
        self.bdata[K_RECORD_LABELS] = [
            "%d-%s" % (a, b) for a, b in self.record_settings
        ]


@ItemSplitterSimpleAction.Listen()
def onSimpleAction(event):
    # type: (ItemSplitterSimpleAction) -> None
    m = SafeGetMachine(event.x, event.y, event.z, event.player_id)
    if not isinstance(m, ItemSplitter):
        return
    if event.action == event.ACTION_ADD_SETTING:
        m.onAddSetting(event.player_id)
    elif event.action == event.ACTION_REMOVE_SETTING:
        m.onDeleteSetting(event.player_id, event.extra)


@ItemSplitterSettingsSetLabel.Listen()
def onSetLabel(event):
    # type: (ItemSplitterSettingsSetLabel) -> None
    m = SafeGetMachine(event.x, event.y, event.z, event.player_id)
    if not isinstance(m, ItemSplitter):
        return
    if not isinstance(event.label, int) or not isinstance(event.setting_index, int):
        return
    m.onSetLabel(event.player_id, event.setting_index, event.label)


@ItemSplitterSettingsSetItem.Listen()
def onSetItem(event):
    # type: (ItemSplitterSettingsSetItem) -> None
    m = SafeGetMachine(event.x, event.y, event.z, event.player_id)
    if not isinstance(m, ItemSplitter):
        return
    if (
        not isinstance(event.setting_index, int)
        or not isinstance(event.item_id, str)
        or len(event.item_id) > 256
    ):
        return
    m.onSetItem(event.player_id, event.setting_index, event.item_id)
