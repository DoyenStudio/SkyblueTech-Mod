# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.id_enum import BrineEvaporationPond
from skybluetech_scripts.skybluetech.common.machinery_def.brine_evaporation_pond import (
    CHAMBER_HEAT_CAPACITY,
    K_FLUID_RENDER_ORIGIN,
    K_FLUID_RENDER_SIZE,
    STRUCTURE_PALETTE,
    recipes,
)
from skybluetech_scripts.skybluetech.server.machinery.basic import (
    GUIControl,
    HeatCtrl,
    MultiBlockStructure,
)
from skybluetech_scripts.skybluetech.server.machinery.core import RegisterMachine
from skybluetech_scripts.skybluetech.server.machinery.interfaces import (
    FluidInputInterface,
    FluidOutputInterface,
    HeatInputInterface,
)


FluidInputInterface.AddExtraMachineId(BrineEvaporationPond.IO_FLUID1)
FluidOutputInterface.AddExtraMachineId(BrineEvaporationPond.IO_FLUID2)
HeatInputInterface.AddExtraMachineId(BrineEvaporationPond.IO_HEAT)
# 显式刷新接口注册表，不依赖控制器类的注册时机。
RegisterMachine(FluidInputInterface)
RegisterMachine(FluidOutputInterface)
RegisterMachine(HeatInputInterface)

recipes_collection = {}
for recipe in recipes:
    recipes_collection.setdefault(recipe.collection_name, []).append(recipe)
for fluid_recipes in recipes_collection.values():
    fluid_recipes.sort(key=lambda recipe: recipe.min_temperature, reverse=True)


@RegisterMachine
class BrineEvaporationPondController(GUIControl, MultiBlockStructure, HeatCtrl):
    block_name = BrineEvaporationPond.CONTROLLER
    is_non_energy_machine = True
    heat_capacity = CHAMBER_HEAT_CAPACITY
    structure_palette = STRUCTURE_PALETTE
    functional_block_ids = {
        BrineEvaporationPond.IO_FLUID1,
        BrineEvaporationPond.IO_FLUID2,
        BrineEvaporationPond.IO_HEAT,
    }

    def __init__(self, dim, x, y, z, block_entity_data):
        super(BrineEvaporationPondController, self).__init__(
            dim, x, y, z, block_entity_data
        )
        self._input_io = None
        self._output_io = None
        self._heat_io = None
        self._update_fluid_render_bounds(False)
        self.handler.SubscribeOnTicking(self._brine_pond_on_ticking)
        self.handler.SubscribeOnStructureChanged(self._brine_pond_on_structure_changed)
        self.handler.SubscribeOnUnload(self.disconnect_ios)
        self.handler.SubscribeOnSync(self._brine_pond_on_sync)
        self.CallSync()

    def _brine_pond_on_ticking(self):
        self.work_once()
        self.CallSync()

    def _brine_pond_on_structure_changed(self, ok):
        self.disconnect_ios()
        self._update_fluid_render_bounds(ok)
        if ok:
            self._refresh_ios()

    def _update_fluid_render_bounds(self, ok):
        # 使用检测器实际旋转后的空腔，渲染与结构朝向保持一致。
        if not ok:
            self.bdata[K_FLUID_RENDER_ORIGIN] = None
            self.bdata[K_FLUID_RENDER_SIZE] = None
            return
        air_poses = self.area.rotated_palette.air_poses
        min_x = min(pos[0] for pos in air_poses)
        min_y = min(pos[1] for pos in air_poses)
        min_z = min(pos[2] for pos in air_poses)
        max_x = max(pos[0] for pos in air_poses) + 1
        max_y = max(pos[1] for pos in air_poses) + 1
        max_z = max(pos[2] for pos in air_poses) + 1
        # 只保存相对坐标，避免世界远处的 float32 精度损失。
        # 列表统一使用 float，满足 BlockEntityData 同型列表的持久化约束。
        self.bdata[K_FLUID_RENDER_ORIGIN] = [
            (min_x + max_x) / 2.0,
            float(min_y),
            (min_z + max_z) / 2.0,
        ]
        self.bdata[K_FLUID_RENDER_SIZE] = [
            float(max_x - min_x),
            float(max_y - min_y),
            float(max_z - min_z),
        ]

    def disconnect_ios(self):
        for machine in (self._input_io, self._output_io, self._heat_io):
            if machine is not None and machine.getMachineRef() is self:
                machine.UnsetMachineRef()
        self._input_io = None
        self._output_io = None
        self._heat_io = None

    def _refresh_ios(self):
        # 每 tick 重新解析接口，避免区块重载后继续操作已卸载的旧实例。
        if not self.StructureFinished():
            self.disconnect_ios()
            return False
        input_io = self.TryGetLoadedMachine(
            FluidInputInterface, BrineEvaporationPond.IO_FLUID1
        )
        output_io = self.TryGetLoadedMachine(
            FluidOutputInterface, BrineEvaporationPond.IO_FLUID2
        )
        heat_io = self.TryGetLoadedMachine(
            HeatInputInterface, BrineEvaporationPond.IO_HEAT
        )
        if input_io is None or output_io is None or heat_io is None:
            self.disconnect_ios()
            return False
        current_ios = (self._input_io, self._output_io, self._heat_io)
        loaded_ios = (input_io, output_io, heat_io)
        if current_ios != loaded_ios:
            self.disconnect_ios()
            self._input_io, self._output_io, self._heat_io = loaded_ios
            for machine in loaded_ios:
                machine.SetMachineRef(self)
        return True

    def _brine_pond_on_sync(self):
        # 控制器的 0/1 号流体字段只供 UI 显示；实际库存始终保存在接口。
        for index, machine in enumerate((self._input_io, self._output_io)):
            fluid = machine.fluids[0] if machine is not None else None
            fluid_id = fluid.fluid_id if fluid is not None else None
            volume = fluid.volume if fluid is not None else 0.0
            id_key = "fluid_id" + str(index)
            volume_key = "fluid_vol" + str(index)
            if self.bdata[id_key] != fluid_id:
                self.bdata[id_key] = fluid_id
            if self.bdata[volume_key] != volume:
                self.bdata[volume_key] = float(volume)

    def work_once(self):
        if not self._refresh_ios() or not self.IsActive():
            return
        input_fluid = self._input_io.fluids[0]
        for recipe in recipes_collection.get(input_fluid.fluid_id, ()):
            # 按最低温度从高到低检查完整加工条件，一 tick 最多处理一条。
            if self.work_with_recipe(recipe):
                break

    def work_with_recipe(self, recipe):
        if self.kelvin <= recipe.min_temperature:
            return False
        rate = min(
            1.0,
            float(self.kelvin - recipe.min_temperature)
            / (recipe.fit_temperature - recipe.min_temperature),
        )
        consume = recipe.consume * rate
        produce = recipe.produce * rate
        heat_cost = recipe.heat_cost * rate
        input_fluid = self._input_io.fluids[0]
        output_fluid = self._output_io.fluids[0]
        if input_fluid.volume < consume or self.heat_value < heat_cost:
            return False
        if not output_fluid.canMerge(recipe.produce_matter):
            return False
        if output_fluid.max_volume - output_fluid.volume < produce:
            return False
        input_id = input_fluid.fluid_id
        input_fluid.volume -= consume
        self.heat_value -= heat_cost
        self._output_io.OutputFluid(recipe.produce_matter, produce, 0, True)
        self._input_io._on_reduced_fluid(0, input_id, consume, True)
        return True
