# coding=utf-8
from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.skybluetech.common.define import flags
from skybluetech_scripts.skybluetech.common.define.id_enum import Machinery
from skybluetech_scripts.skybluetech.common.machinery_def.fuel_heater import (
    FUEL_HEAT_MULTIPLIER,
    FUEL_SECONDS_MAP,
    K_BURN_SEC_LEFT,
    K_MAX_BURN_SEC,
    MAX_HEAT_VALUE,
    MAX_KELVIN,
    SECOND_PER_TICK,
    TICK_POWER,
)
from skybluetech_scripts.skybluetech.server.machinery.basic import (
    GUIControl,
    HeatCtrl,
    ItemContainer,
    WorkRenderer,
)
from skybluetech_scripts.skybluetech.server.machinery.core import RegisterMachine


@RegisterMachine
class FuelHeater(WorkRenderer, GUIControl, ItemContainer, HeatCtrl):
    """燃料直接产热，燃烧时长与火力发电机相同，电热路线的热量乘四。"""

    block_name = Machinery.FUEL_HEATER
    is_non_energy_machine = True
    store_rf_max = 0
    energy_io_mode = (2, 2, 2, 2, 2, 2)
    item_input_slots = (0,)
    max_heat_value = MAX_HEAT_VALUE
    spread_heat = True

    def __init__(self, dim, x, y, z, block_entity_data):
        super(FuelHeater, self).__init__(dim, x, y, z, block_entity_data)
        self.handler.SubscribeOnHeatWork(self._fuel_heater_on_heat_work)
        # 燃尽后可能尚未刷新外观就卸载；重载时强制与燃料余量对齐一次。
        self._last_work_status = None
        if self.burn_seconds_left <= 0:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT, flush=False)
        else:
            self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT, flush=False)
        self.FlushDeactiveFlags()

    def IsValidInput(self, slot, item):
        # type: (int, Item) -> bool
        return slot in self.item_input_slots and self._get_burn_seconds(item) > 0

    @staticmethod
    def _get_burn_seconds(item):
        # type: (Item | None) -> float
        if item is None or item.count <= 0 or item.newItemName == "minecraft:lava_bucket":
            return 0.0
        return float(FUEL_SECONDS_MAP.get(item.id) or item.GetBasicInfo().fuelDuration)

    def _fuel_heater_on_heat_work(self):
        # type: () -> None
        self.SetOutputHeatPower(0.0)
        if not self.IsActiveIgnoreCondition(flags.DEACTIVE_FLAG_NO_INPUT):
            return
        if self.kelvin >= self.heat_target_kelvin:
            return
        if self.burn_seconds_left <= 0 and not self._start_next_fuel():
            return
        self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT)
        burn_seconds = min(
            self.burn_seconds_left, self.WORK_INTERVAL * SECOND_PER_TICK
        )
        # HeatCtrl 每 WORK_INTERVAL tick 施热一次，末周期只结算剩余燃烧时长。
        electric_equivalent = TICK_POWER * burn_seconds / SECOND_PER_TICK
        self.SetOutputHeatPower(
            self.HeatFromElectric(electric_equivalent) * FUEL_HEAT_MULTIPLIER
        )
        self.burn_seconds_left = max(0.0, self.burn_seconds_left - burn_seconds)
        # 此回调后 HeatCtrl 才施热；燃尽停机留到下周期，避免丢掉最后一份热。
        # 与电力加热仓一致，逼近目标温度时超出的本周期热量由 HeatCtrl 舍弃。

    def _start_next_fuel(self):
        # type: () -> bool
        item = self.GetSlotItem(0)
        burn_seconds = self._get_burn_seconds(item)
        if burn_seconds <= 0:
            if not self.HasDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT):
                self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT)
            return False
        item.count -= 1
        if not self.SetSlotItem(0, item if item.count > 0 else None):
            return False
        self.burn_seconds_left = burn_seconds
        self.bdata[K_MAX_BURN_SEC] = burn_seconds
        return True

    @property
    def heat_target_kelvin(self):
        # type: () -> float
        return float(MAX_KELVIN)

    @property
    def burn_seconds_left(self):
        # type: () -> float
        return max(0.0, float(self.bdata[K_BURN_SEC_LEFT] or 0.0))

    @burn_seconds_left.setter
    def burn_seconds_left(self, value):
        # type: (float) -> None
        # 原生浮点随每次热结算保存，卸载无需另补缓存，UI 与存档共用该值。
        self.bdata[K_BURN_SEC_LEFT] = float(value)
