# coding=utf-8
"""蒸馏塔控制器、接口绑定与输出库存显示快照。"""

from skybluetech_scripts.skybluetech.common.define.id_enum import DistillationColumn
from skybluetech_scripts.skybluetech.common.define import flags
from skybluetech_scripts.skybluetech.server.machinery.core import RegisterMachine
from skybluetech_scripts.skybluetech.server.machinery.interfaces import (
    FluidInputInterface,
    FluidOutputInterface,
    HeatInputInterface,
)
from skybluetech_scripts.skybluetech.common.machinery_def.distillation_column import (
    CHAMBER_HEAT_CAPACITY, INPUT_MAX_VOLUME, K_OUTPUT_CAPACITY,
    K_OUTPUT_COUNT, MAX_OUTPUT_PORTS, MIN_OUTPUT_PORTS, STRUCTURE_PALETTE, recipes,
)
from skybluetech_scripts.skybluetech.common.machinery_def.basic.multi_fluid_container import FLUID_VOLUME_EPSILON
from skybluetech_scripts.skybluetech.server.machinery.basic import (
    GUIControl, HeatCtrl, MultiBlockStructure, MultiFluidContainer,
)
from skybluetech_scripts.skybluetech.server.machinery.core.pool import GetLoadedMachine


FluidInputInterface.AddExtraMachineId(DistillationColumn.IO_FLUID1)
FluidOutputInterface.AddExtraMachineId(DistillationColumn.IO_FLUID2)
HeatInputInterface.AddExtraMachineId(DistillationColumn.IO_HEAT)
# 显式刷新接口注册表，不依赖控制器类的注册时机。
RegisterMachine(FluidInputInterface)
RegisterMachine(FluidOutputInterface)
RegisterMachine(HeatInputInterface)

IDLE_FLAGS = (flags.DEACTIVE_FLAG_NO_INPUT, flags.DEACTIVE_FLAG_NO_RECIPE,
              flags.DEACTIVE_FLAG_FLUID_FULL, flags.DEACTIVE_FLAG_FLUID_NOT_MATCH)
IDLE_MASK = 0
for _flag in IDLE_FLAGS:
    IDLE_MASK |= _flag

@RegisterMachine
class DistillationColumnController(GUIControl, MultiBlockStructure, MultiFluidContainer, HeatCtrl):
    block_name = DistillationColumn.CONTROLLER
    is_non_energy_machine = True
    heat_capacity = CHAMBER_HEAT_CAPACITY
    structure_palette = STRUCTURE_PALETTE
    functional_block_ids = {DistillationColumn.IO_HEAT, DistillationColumn.IO_FLUID1, DistillationColumn.IO_FLUID2}
    fluid_io_fix_mode = 0
    fluid_input_slots = (0,)
    fluid_output_slots = ()
    fluid_slot_max_volumes = {0: INPUT_MAX_VOLUME}

    def __init__(self, dim, x, y, z, block_entity_data):
        super(DistillationColumnController, self).__init__(dim, x, y, z, block_entity_data)
        self._input_ios = []
        self._output_ios = []
        self._heat_ios = []
        self._working = False
        self.handler.SubscribeOnTicking(self._column_on_tick)
        self.handler.SubscribeOnStructureChanged(self._column_on_structure_changed)
        self.handler.SubscribeOnUnload(self.disconnect_ios)
        self.handler.SubscribeOnSync(self._column_on_sync)
        self.CallSync()

    def disconnect_ios(self):
        for machine in self._input_ios + self._output_ios + self._heat_ios:
            if machine.getMachineRef() is self:
                machine.UnsetMachineRef()
        self._input_ios = []
        self._output_ios = []
        self._heat_ios = []

    def _column_on_structure_changed(self, ok):
        self.disconnect_ios()
        self._column_on_sync()

    def _refresh_ios(self):
        if not self.StructureFinished():
            self.disconnect_ios()
            return False
        poses = self.GetFunctionalBlockPoses()
        # 先按世界坐标选出最高四口，再解析实例；未加载的高口不能被低口顶替。
        output_poses = sorted(
            poses.get(DistillationColumn.IO_FLUID2, ()),
            key=lambda pos: (-pos[1], pos[0], pos[2]),
        )[:MAX_OUTPUT_PORTS]
        output_ios = [GetLoadedMachine(self.dim, *pos) for pos in output_poses]
        input_ios = self.GetAllMachines(FluidInputInterface, DistillationColumn.IO_FLUID1)
        heat_ios = self.GetAllMachines(HeatInputInterface, DistillationColumn.IO_HEAT)
        if (len(output_ios) < MIN_OUTPUT_PORTS
                or any(not isinstance(m, FluidOutputInterface) for m in output_ios)
                or len(input_ios) != len(poses.get(DistillationColumn.IO_FLUID1, ()))
                or len(heat_ios) != len(poses.get(DistillationColumn.IO_HEAT, ()))):
            self.disconnect_ios()
            return False
        input_ios.sort(key=lambda machine: machine.xyz)
        heat_ios.sort(key=lambda machine: machine.xyz)
        all_ios = input_ios + output_ios + heat_ios
        if any(m.getMachineRef() not in (None, self) for m in all_ios):
            self.disconnect_ios()
            return False
        if (input_ios, output_ios, heat_ios) != (self._input_ios, self._output_ios, self._heat_ios):
            self.disconnect_ios()
            self._input_ios, self._output_ios, self._heat_ios = input_ios, output_ios, heat_ios
            for machine in all_ios:
                machine.SetMachineRef(self)
        return True

    def _column_on_tick(self):
        if self._working:
            return
        self._working = True
        try:
            self._tick_work()
        finally:
            self._working = False

    def _tick_work(self):
        if self._refresh_ios():
            target = self.fluids[0]
            for machine in self._input_ios:
                source = machine.fluids[0]
                fluid_id = source.fluid_id
                if not target.canMerge(fluid_id):
                    continue
                amount = min(source.volume, target.max_volume - target.volume)
                if amount <= FLUID_VOLUME_EPSILON:
                    continue
                # 两端先提交，再发更新事件；实际库存不放在显示快照中。
                target.fluid_id = fluid_id
                target.volume += amount
                source.volume -= amount
                self._on_added_fluid(0, fluid_id, amount, True)
                machine._on_reduced_fluid(0, fluid_id, amount, True)
            if self.IsActiveIgnoreCondition(IDLE_MASK):
                reason = self.work_once()
                for flag in IDLE_FLAGS:
                    self.UpdateDeactiveFlag(flag, flag == reason)
        self._write_output_snapshot()

    def work_once(self):
        # 每 tick 重新按当前原料、温度选择，不把配方锁在过期温区。
        source = self.fluids[0]
        if source.fluid_id is None or source.volume <= FLUID_VOLUME_EPSILON:
            return flags.DEACTIVE_FLAG_NO_INPUT
        for recipe in recipes:
            if recipe.collection_name != source.fluid_id:
                continue
            plan = recipe.evaluate(self.kelvin)
            if plan is not None:
                return self._commit_recipe(recipe, plan)
        return flags.DEACTIVE_FLAG_NO_RECIPE

    def _commit_recipe(self, recipe, plan):
        source = self.fluids[0]
        # 输入、供热允许降低吞吐；输出不足则整批暂停，不靠丢弃已绑定口的产物腾空间。
        scale = min(1.0, source.volume / plan.feed_volume)
        if plan.heat_cost > 0.0:
            available_heat = max(0.0, self.heat_value - self.heat_capacity * recipe.min_temperature)
            scale = min(scale, available_heat / plan.heat_cost)
        plan = plan.scaled(scale)
        if plan.feed_volume <= FLUID_VOLUME_EPSILON:
            return flags.DEACTIVE_FLAG_NO_RECIPE
        updates = []
        for machine, fluid_id, volume in zip(self._output_ios, recipe.output_fluids, plan.output_volumes):
            target = machine.fluids[0]
            # 该配方使用的口已满，即使当前温度下对应馏分为零也暂停。
            if target.isFull() or target.max_volume - target.volume < volume:
                return flags.DEACTIVE_FLAG_FLUID_FULL
            if volume <= 0.0:
                continue
            if target.fluid_id not in (None, fluid_id):
                return flags.DEACTIVE_FLAG_FLUID_NOT_MATCH
            # 槽位会清除 <= epsilon 的微量液体，不能将这种写入视为成功产出。
            if target.volume + volume <= FLUID_VOLUME_EPSILON:
                return flags.DEACTIVE_FLAG_NO_RECIPE
            updates.append((machine, fluid_id, volume))
        # zip 截去缺口对应的重馏分/残液：主动丢弃，但完整扣取其原料与蒸馏热耗。
        input_id = source.fluid_id
        source.volume -= plan.feed_volume
        for machine, fluid_id, volume in updates:
            target = machine.fluids[0]
            target.fluid_id = fluid_id
            target.volume += volume
        self.heat_value -= plan.heat_cost
        # 全部状态提交后才发送回调，避免观察到半次加工。
        self._on_reduced_fluid(0, input_id, plan.feed_volume, True)
        for machine, fluid_id, volume in updates:
            machine._on_added_fluid(0, fluid_id, volume, True)
        return 0

    def _column_on_sync(self):
        self._refresh_ios()
        self._write_output_snapshot()

    def _write_output_snapshot(self):
        snapshot = {K_OUTPUT_COUNT: len(self._output_ios)}
        for index in range(MAX_OUTPUT_PORTS):
            fluid = self._output_ios[index].fluids[0] if index < len(self._output_ios) else None
            suffix = str(index + 1)
            # 槽 1..4 仅为客户端兼容 FluidSlotClient 的显示字段，绝不创建 FluidSlotServer。
            snapshot["fluid_id" + suffix] = fluid.fluid_id if fluid else None
            snapshot["fluid_vol" + suffix] = float(fluid.volume) if fluid else 0.0
            snapshot[K_OUTPUT_CAPACITY + suffix] = float(fluid.max_volume) if fluid else 1.0
        for key, value in snapshot.items():
            if self.bdata[key] != value:
                self.bdata[key] = value
