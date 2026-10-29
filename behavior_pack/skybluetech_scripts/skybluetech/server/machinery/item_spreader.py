# coding=utf-8
from skybluetech_scripts.tooldelta.define.item import Item

from .basic.item_container import ItemContainer
from ...common.define import flags
from ...common.define.id_enum import Machinery, Upgraders
from ...common.machinery_def.item_spreader import (
    K_NUM_CONTAINERS,
    K_SPREADER_POINTER,
    POWER_COST_ONCE,
    STORE_RF_MAX,
    TICK_DURATION,
)
from ..transmitters.item_pipe.logic import (
    PushItemToGenericContainer,
)
from ..transmitters.item_pipe.logic import (
    logic_module as item_pipe_logic,
)
from .basic import (
    BaseSpeedControl,
    GUIControl,
    OperationListener,
    UpgradeControl,
)
from .core import RegisterMachine


@RegisterMachine
class ItemSpreader(UpgradeControl, OperationListener, GUIControl):
    block_name = Machinery.ITEM_SPREADER
    item_input_slots = (0,)
    item_output_slots = ()
    store_rf_max = STORE_RF_MAX
    running_power = POWER_COST_ONCE
    origin_process_ticks = TICK_DURATION
    upgrade_slot_start = 1
    upgrade_slots = 4
    allow_upgraders = frozenset({
        Upgraders.BASIC_SPEED_UPGRADER,
        Upgraders.BASIC_ENERGY_UPGRADER,
    })

    def __init__(self, dim, x, y, z, block_entity_data):
        super(ItemSpreader, self).__init__(dim, x, y, z, block_entity_data)
        self._all_input_access_points = []
        self._working = False
        self._dirty = True
        self._empty = False
        self._fail_streak = 0  # 连续投递失败次数; 一整轮容器都放不进才算输出受阻 (个别容器满了不算)
        self.handler.SubscribeOnTicking(self._item_spreader_on_ticking)
        self.handler.SubscribeOnSlotUpdate(self._item_spreader_on_slot_update)
        self.handler.SubscribeOnInvalidateCaches(self._item_spreader_on_invalidate_caches)

    def _item_spreader_on_ticking(self):
        if self._dirty:
            self.update_acceess_points()
            self._dirty = False
        # 状态灯: 没有物品 = 缺少输入, 能量不够投递一次 = 能量不足 (投递失败的原因在 spread 里设)
        self.UpdateDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT, self._empty)
        if self._empty:
            self._fail_streak = 0
            self.UpdateDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL, False)
            return
        power_enough = self.store_rf >= self.running_power
        self.UpdateDeactiveFlag(flags.DEACTIVE_FLAG_POWER_LACK, not power_enough)
        if BaseSpeedControl.ProcessOnce(self) and power_enough:
            self.spread()

    def _item_spreader_on_slot_update(self, slot):
        if slot == 0:
            self._empty = self.GetSlotItem(0) is None

    def _item_spreader_on_invalidate_caches(self):
        self._dirty = True

    def IsValidInput(self, slot, item):
        # type: (int, Item) -> bool
        results = (
            ItemContainer.IsValidInput(self, slot, item),
            UpgradeControl.IsValidInput(self, slot, item),
            self._item_spreader_is_valid_input(slot, item),
        )
        return all(results)

    def _item_spreader_is_valid_input(self, slot, item):
        if self.InUpgradeSlot(slot):
            return UpgradeControl.IsValidInput(self, slot, item)
        return slot == 0

    def update_acceess_points(self):
        output_networks = (
            item_pipe_logic
            .GetContainerNode(self.dim, self.x, self.y, self.z)
            .get_outputs()
            .values()
        )
        self._all_input_access_points = sorted(
            (
                ap
                for network in output_networks
                for ap in network.get_input_access_points()
            ),
            key=lambda x: x.get_priority(),
        )
        self.num_containers = len(self._all_input_access_points)
        if self.num_containers <= 0:
            self.spreader_pointer = 0
        else:
            self.spreader_pointer %= self.num_containers

    def spread(self):
        ap = self._next_acceess_point()
        if ap is None:
            # 没有连接任何可投递的容器
            self.UpdateDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL, True)
            return
        item = self.GetSlotItem(0)
        if item is None:
            self._empty = True
            return
        item_new = item.copy()
        item_new.count = 1
        rest = PushItemToGenericContainer(ap, item_new)
        if rest is None:
            new_count = item.count - 1
        else:
            new_count = item.count - (item_new.count - rest.count)
        moved = new_count != item.count
        if moved:
            item.count = new_count
            self.SetSlotItem(0, item)
            self.ReducePower(self.running_power)
            self._fail_streak = 0
        else:
            self._fail_streak += 1
        self.UpdateDeactiveFlag(
            flags.DEACTIVE_FLAG_OUTPUT_FULL,
            self._fail_streak >= len(self._all_input_access_points),
        )

    def _next_acceess_point(self):
        access_points_num = len(self._all_input_access_points)
        if access_points_num == 0:
            self.num_containers = 0
            self.spreader_pointer = 0
            return None
        self.num_containers = access_points_num
        ptr = self.spreader_pointer % access_points_num
        ap = self._all_input_access_points[ptr]
        self.spreader_pointer = (ptr + 1) % access_points_num
        return ap

    @property
    def num_containers(self):
        # type: () -> int
        return self.bdata[K_NUM_CONTAINERS] or 0

    @num_containers.setter
    def num_containers(self, value):
        # type: (int) -> None
        self.bdata[K_NUM_CONTAINERS] = value

    @property
    def spreader_pointer(self):
        # type: () -> int
        return self.bdata[K_SPREADER_POINTER] or 0

    @spreader_pointer.setter
    def spreader_pointer(self, value):
        # type: (int) -> None
        self.bdata[K_SPREADER_POINTER] = value
