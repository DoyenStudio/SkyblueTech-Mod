# coding=utf-8
#
from mod.server.blockEntityData import BlockEntityData
from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.api.common import ExecLater
from ...common.define import flags
from ...common.define.id_enum import BATTERY_MATRIX_CORE as MACHINE_ID
from ...common.define.tag_enum import BatteryTag
from ...common.events.machinery.battery_matrix import BatteryMatrixCoreStatusUpdate
from .basic import (
    BaseMachine,
    ItemContainer,
    RegisterMachine,
)
from .utils.charge import GetCharge, UpdateCharge, GetOutputPower

INFINITY = float("inf")


@RegisterMachine
class BatteryMatrixCore(BaseMachine, ItemContainer):
    block_name = MACHINE_ID
    store_rf_max = 1
    input_slots = tuple(range(27))
    is_non_energy_machine = True  # 以防被直接接入电网

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        BaseMachine.__init__(self, dim, x, y, z, block_entity_data)
        ItemContainer.__init__(self, dim, x, y, z, block_entity_data)
        self.slots = []  # type: list[BatterySlotAbstract]
        self.update_core_data()
        self._is_cleaning_slot = False

    def IsValidInput(self, slot, item):
        # type: (int, Item) -> bool
        return BatteryTag.COMMON in item.GetBasicInfo().tags

    def OnSlotUpdate(self, slot_pos):
        if self._is_cleaning_slot:
            return
        self.update_core_data()

    def gen_update_event(self, first=False):
        return BatteryMatrixCoreStatusUpdate(
            [(i.item_id, i.store_rf, i.store_rf_max) for i in self.slots], first
        )

    def clean_slots(self):
        self._is_cleaning_slot = True
        slotitems = [i for i in self.GetInputSlotItems().values() if i is not None]
        final_slotitems = {
            i: slotitems[i] if i < len(slotitems) else None for i in self.input_slots
        }
        self.SetSlotItems(final_slotitems)
        self._is_cleaning_slot = False

    def core_tick(self):
        # type: () -> None
        self.save_core_data()

    def calculate_core_store_rf(self):
        return sum(i.store_rf for i in self.slots)

    def calculate_core_store_rf_max(self):
        return sum(i.store_rf_max for i in self.slots)

    def update_core_data(self):
        self.slots = []
        self.clean_slots()
        for slot in self.input_slots:
            item = self.GetSlotItem(slot, get_user_data=True)
            if item is None:
                continue
            self.slots.append(BatterySlotAbstract.load_from_item(item))

    def save_core_data(self):
        for slot, bs in enumerate(self.slots):
            if not bs.is_changed():
                continue
            it = self.GetSlotItem(slot)
            if it is None:
                continue
            bs.save_to_item(it)
            self.SetSlotItem(slot, it)

    def add_energy(self, rf, from_overflow=False):
        # type: (int, bool) -> int
        for bs in self.slots:
            rf = bs.add_rf(rf)
        return rf

    def output_energy(self):
        1
        # TODO: SLOW!!!
        return sum(bs.output_rf() for bs in self.slots)


class BatterySlotAbstract(object):
    def __init__(self, item_id, store_rf, store_rf_max, output_power):
        # type: (str, int, int, int) -> None
        self._orig_store_rf = self.store_rf = store_rf
        self.item_id = item_id
        self.store_rf_max = store_rf_max
        self.output_power = output_power

    @classmethod
    def load_from_item(
        cls,
        item,  # type: Item
    ):
        ud = item.userData or {}
        charge, charge_max = GetCharge(ud)
        output_power = GetOutputPower(ud)
        return cls(item.id, charge, charge_max, output_power)

    def save_to_item(self, item, owner=None):
        # type: (Item, str | None) -> None
        ud = item.userData
        if not ud:
            return
        UpdateCharge(owner or "", item, self.store_rf)
        self._orig_store_rf = self.store_rf

    def add_rf(self, rf):
        # type: (int) -> int
        overflow = max(0, self.store_rf + rf - self.store_rf_max)
        self.store_rf = min(self.store_rf + rf, self.store_rf_max)
        return overflow

    def output_rf(self):
        rf = min(self.store_rf, self.output_power)
        self.store_rf -= rf
        return rf

    def is_changed(self):
        return self.store_rf != self._orig_store_rf
