# coding=utf-8
from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.api.server import (
    GetBlockEntityDataDict,
    SetBlockEntityData,
    SpawnDroppedItem,
)
from skybluetech_scripts.tooldelta.extensions import item_nbt
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ...common.define.id_enum import BATTERY_MATRIX_CORE as MACHINE_ID
from ...common.events.machinery.battery_matrix import BatteryMatrixCoreStatusUpdate
from .basic import (
    BaseMachine,
    RegisterMachine,
)
from .utils.charge import GetCharge, UpdateCharge, GetIOPower, UpdateChargeNBT

K_ITEMS = "st:items"


@RegisterMachine
class BatteryMatrixCore(BaseMachine):
    block_name = MACHINE_ID
    store_rf_max = 1
    slots_num = 27
    is_non_energy_machine = True  # 以防被直接接入电网

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        self.slots = []  # type: list[BatterySlotAbstract]
        self.update_core_data()
        self._is_cleaning_slot = False

    def OnDestroy(self):
        blocknbt = GetBlockEntityDataDict(self.dim, (self.x, self.y, self.z))
        if blocknbt is None:
            return None
        exData = blocknbt["exData"]
        items = exData.get(K_ITEMS, [])  # type: list[dict]
        for item_inbt in items:
            SpawnDroppedItem(
                self.dim, (self.x, self.y, self.z), item_nbt.INBT2Item(item_inbt)
            )

    def add_battery(self, battery):
        # type: (Item) -> bool
        self.save_core_data()
        blocknbt = GetBlockEntityDataDict(self.dim, (self.x, self.y, self.z))
        if blocknbt is None:
            return False
        exData = blocknbt["exData"]
        items = exData.get(K_ITEMS, [])  # type: list[dict]
        if len(items) >= self.slots_num:
            return False
        items.append(item_nbt.Item2INBT(battery))
        exData[K_ITEMS] = items
        SetBlockEntityData(self.dim, (self.x, self.y, self.z), blocknbt)
        self.update_core_data()
        return True

    def pop_battery(self, index):
        # type: (int) -> Item | None
        self.save_core_data()
        blocknbt = GetBlockEntityDataDict(self.dim, (self.x, self.y, self.z))
        if blocknbt is None:
            return None
        exData = blocknbt["exData"]
        items = exData.get(K_ITEMS, [])  # type: list[dict]
        if index >= len(items) or index < 0:
            return
        item = item_nbt.INBT2Item(items.pop(index))
        exData[K_ITEMS] = items
        SetBlockEntityData(self.dim, (self.x, self.y, self.z), blocknbt)
        self.update_core_data()
        return item

    def gen_update_event(self, first=False):
        return BatteryMatrixCoreStatusUpdate(
            [(v.item_id, v.store_rf, v.store_rf_max) for v in self.slots],
            first,
        )

    def core_tick(self):
        # type: () -> None
        self.save_core_data()

    def calculate_core_store_rf(self):
        return sum(i.store_rf for i in self.slots)

    def calculate_core_store_rf_max(self):
        return sum(i.store_rf_max for i in self.slots)

    def update_core_data(self):
        self.slots = []
        block_nbt = GetBlockEntityDataDict(self.dim, (self.x, self.y, self.z))
        if block_nbt is None:
            return
        exData = block_nbt["exData"]
        for item_inbt in exData.get(K_ITEMS, []):
            item = item_nbt.INBT2Item(item_inbt)
            userdata = item.userData
            if userdata is None:
                continue
            self.slots.append(
                BatterySlotAbstract.load_from_item_userdata(item.id, userdata)
            )

    def save_core_data(self):
        block_nbt = GetBlockEntityDataDict(self.dim, (self.x, self.y, self.z))
        if block_nbt is None:
            return
        exData = block_nbt["exData"]
        for slot, item in enumerate(exData.get(K_ITEMS, [])):
            userdata = item.get(item_nbt.INBTKey.USER_DATA, {})
            bs = self.slots[slot]
            if bs is None or not bs.is_changed():
                continue
            bs.save_to_item_userdata(userdata)
        SetBlockEntityData(self.dim, (self.x, self.y, self.z), block_nbt)

    def add_energy(self, rf, from_overflow=False):
        # type: (int, bool) -> int
        for bs in self.slots:
            rf = bs.add_rf(rf)
        return rf

    def output_energy(self, max_rf):
        # type: (int | None) -> int
        if max_rf is None:
            return sum(bs.output_rf() for bs in self.slots)
        else:
            output_rf = 0
            for bs in self.slots:
                rf = bs.output_rf(max_rf - output_rf)
                output_rf += rf
                if output_rf >= max_rf:
                    break
            return output_rf


class BatterySlotAbstract(object):
    def __init__(self, item_id, store_rf, store_rf_max, input_power, output_power):
        # type: (str, int, int, int, int) -> None
        self._orig_store_rf = self.store_rf = store_rf
        self.item_id = item_id
        self.store_rf_max = store_rf_max
        self.input_power = input_power
        self.output_power = (
            output_power * 5
        )  # TODO: 规范化代码, 因为机器的输出 tick 是 5t 所以单次最大输出要乘以 5

    @classmethod
    def load_from_item_userdata(
        cls,
        item_id,  # type: str
        ud,  # type: dict
    ):
        charge, charge_max = GetCharge(ud)
        input_power, output_power = GetIOPower(ud)
        return cls(item_id, charge, charge_max, input_power, output_power)

    def save_to_item(self, item, owner=None):
        # type: (Item, str | None) -> None
        ud = item.userData
        if not ud:
            return
        UpdateCharge(item, self.store_rf)
        self._orig_store_rf = self.store_rf

    def save_to_item_userdata(self, ud, owner=None):
        # type: (dict, str | None) -> None
        UpdateChargeNBT(self.item_id, ud, self.store_rf)
        self._orig_store_rf = self.store_rf

    def add_rf(self, rf):
        # type: (int) -> int
        power_in = min(self.input_power, rf)
        power_in_overflow = rf - power_in
        charge_in = min(power_in, self.store_rf_max - self.store_rf)
        charge_in_overflow = power_in - charge_in
        self.store_rf += charge_in
        return power_in_overflow + charge_in_overflow

    def output_rf(self, max_rf=None):
        # type: (int | None) -> int
        if max_rf is None:
            rf = min(self.store_rf, self.output_power)
        else:
            rf = min(self.store_rf, self.output_power, max_rf)
        self.store_rf -= rf
        return rf

    def is_changed(self):
        return self.store_rf != self._orig_store_rf
