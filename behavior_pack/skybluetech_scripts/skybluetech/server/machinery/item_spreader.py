# coding=utf-8
from skybluetech_scripts.tooldelta.api.common import ExecLater
from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta

from ...common.define.id_enum.machinery import Machinery
from ...common.machinery_def.item_spreader import (
    K_NUM_CONTAINERS,
    K_SPREADER_POINTER,
    POWER_COST_ONCE,
    STORE_RF_MAX,
    TICK_DURATION,
)
from ..transmitters.cable.logic import (
    PushItemToGenericContainer,
)
from ..transmitters.cable.logic import (
    logic_module as cable_logic,
)
from .basic import (
    BaseSpeedControl,
    GUIControl,
    OperationListener,
    RegisterMachine,
    UpgradeControl,
)


@RegisterMachine
class ItemSpreader(GUIControl, OperationListener, UpgradeControl):
    block_name = Machinery.ITEM_SPREADER
    input_slots = (0,)
    output_slots = ()
    store_rf_max = STORE_RF_MAX
    running_power = POWER_COST_ONCE
    origin_process_ticks = TICK_DURATION
    upgrade_slot_start = 1
    upgrade_slots = 4
    allow_upgrader_tags = {
        "skybluetech:upgraders/speed",
        "skybluetech:upgraders/energy",
    }

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        self._all_input_access_points = []
        self._working = False
        self._dirty = True
        self._empty = False

    def OnTicking(self):
        if self._dirty:
            self.update_acceess_points()
            self._dirty = False
        if self._empty:
            return
        if BaseSpeedControl.ProcessOnce(self) and self.store_rf >= self.running_power:
            self.spread()

    @SuperExecutorMeta.execute_super
    def OnSlotUpdate(self, slot):
        if slot == 0:
            self._empty = self.GetSlotItem(0) is None

    @SuperExecutorMeta.execute_super
    def OnInvalidateCaches(self):
        self._dirty = True

    def IsValidInput(self, slot, item):
        if self.InUpgradeSlot(slot):
            return UpgradeControl.IsValidInput(self, slot, item)
        return slot == 0

    def update_acceess_points(self):
        output_networks = (
            cable_logic
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
            new_count = item_new.count - rest.count
        if new_count != item.count:
            item.count = new_count
            self.SetSlotItem(0, item)
            self.ReducePower(self.running_power)

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
