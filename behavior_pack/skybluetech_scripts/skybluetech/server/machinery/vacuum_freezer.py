# coding=utf-8
import math

from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta

from ...common.define.id_enum import Machinery
from ...common.define.id_enum import Upgraders
from ...common.define.id_enum import VacuumFreezer as ids
from ...common.events.machinery.vacuum_freezer import VacuumFreezerSubmitModifiesEvent
from ...common.machinery_def.vacuum_freezer import (
    ALL_RECIPES,
    CHAMBER_HEAT_CAPACITY,
    COLD_HEAD_EFFICIENCY,
    EVAPORATOR_APPROACH,
    K_EXPECTED_KELVIN,
    K_MAX_POWER,
    K_RECIPE,
    MAX_EXPECTED_KELVIN,
    MAX_FLUID_VOLUMES,
    MAX_POWER,
    MAX_TICK_COOLDOWN_RATE,
    MIN_EXPECTED_KELVIN,
    RECIPES_NEED_UPGRADERS,
    STORE_RF_MAX,
    STRUCTURE_PALETTE,
    clamp_expected_kelvin,
    clamp_power,
)
from ...common.machinery_def.vacuum_freezer import (
    recipes as Recipes,
)
from ...common.machinery_def.vacuum_freezer import (
    upgrader_recipes as UpgraderRecipes,
)
from ...common.mini_jei.machinery import MachineRecipeBase
from ...common.mini_jei.machinery.vacuum_freezer import VacuumFreezerRecipe
from ...common.utils.phys_math import Thermal
from .basic import (
    HeatCtrl,
    MultiBlockStructure,
    MultiFluidContainer,
    OperationListener,
    Processor,
    RegisterMachine,
)
from .interfaces import (
    EnergyInputInterface,
    FluidInputInterface,
    FluidOutputInterface,
    ItemInputInterface,
    ItemOutputInterface,
)

EnergyInputInterface.AddExtraMachineId(ids.IO_ENERGY)
FluidInputInterface.AddExtraMachineId(ids.IO_FLUID1)
FluidOutputInterface.AddExtraMachineId(ids.IO_FLUID2)
ItemInputInterface.AddExtraMachineId(ids.IO_ITEM1)
ItemOutputInterface.AddExtraMachineId(ids.IO_ITEM2)


@RegisterMachine
class VacuumFreezer(
    HeatCtrl,
    MultiBlockStructure,
    MultiFluidContainer,
    Processor,
    OperationListener,
):
    # 玩家设定目标温度(`expected_kelvin`, K)与最大功率(`max_power`, RF/t), 机器每个
    # 热力结算周期(`HeatCtrl.WORK_INTERVAL` tick)以卡诺制冷机
    # (`phys_math.Thermal.ActiveCool`)把本机温度压向目标温度。

    # 与 `ElectricHeater` 的"耗电产热"相反, 本机是"耗电降温": 移热速率由机器本身的
    # `MAX_TICK_COOLDOWN_RATE` 决定, 而耗电由卡诺 COP 给出 —— 温度越低, 移走同样多的
    # 热量需要的电越多。`COLD_HEAD_EFFICIENCY` 与 `EVAPORATOR_APPROACH` 是两个现实
    # 修正: 前者是冷头相对理想卡诺的效率折扣, 后者是蒸发器温差 —— 本机温度最多只能
    # 逼近它, 温差越大每份热量也越贵。玩家设定的最大功率是每个周期的电能预算,
    # 所以设得太小时机器在低温段会越降越慢, 甚至冻不到设定温度。

    # 仓体的热容由 `CHAMBER_HEAT_CAPACITY` 给出, 远大于全局默认的 1.0 RF/K: 仓里装的
    # 是一整仓要降温的物质, 温度每降 1K 都要搬走 500 RF 的热量, 从环境温度降到液化
    # 温度总共要几十万 RF, 这才是本机耗电的大头。

    # 配方也在这个仓里跑(`VacuumFreezerRecipe`): 压缩空气液化会放热, 放出的热量同样
    # 由制冷机搬走。设计工况是 80K 附近的液化配方, 此时制冷机的 COP(含冷头效率与
    # 蒸发器温差)恰好约 0.1, 即每 1 RF 的放热要花约 10 RF 的电, 也就是约 400 RF/t。

    # 结构里的接口方块不参与热力与配方结算, 只负责搬运物料, 而且流体与物品都是被动
    # 触发的, 不做轮询:

    #     - 输入口一有变动, 就把里面的东西抽进本机(输入口的 `OnSlotUpdate` /
    #       `OnFluidSlotUpdate` 钩子)
    #     - 本机产出槽一有变动, 就把产出推给输出口(本机的 `OnSlotUpdate` /
    #       `OnFluidSlotUpdate`)
    #     - 输出口腾出空间时(最常见的是被管道抽走), 由输出口的钩子再推一次

    # 接口方块全都不参与结构校验, 不放也照样能成型; 只放输入口、只放输出口都可以。
    # 结构刚成型时 `connect_ios()` 会先把接口里已经有的东西补搬一遍, 之后完全由事件
    # 驱动。接口的流体回调是当场触发的, 而搬运自己又会写接口槽位, 所以流体吞吐要带
    # 重入保护, 见 `transmit_fluids`。

    block_name = Machinery.VACUUM_FREEZER
    store_rf_max = STORE_RF_MAX
    heat_capacity = CHAMBER_HEAT_CAPACITY
    # 本机热容远大于默认值, 所以搬运同样的温区要耗多得多的电, 见 CHAMBER_HEAT_CAPACITY
    recipes = Recipes  # pyright: ignore[reportAssignmentType]
    allow_upgraders = (
        Processor.allow_upgraders - {Upgraders.BASIC_SPEED_UPGRADER}
    ) | frozenset(upgrader for upgrader, _ in RECIPES_NEED_UPGRADERS)
    # 只有配方表里真的标了 `extra_upgrader_id` 的升级卡才允许插进来。现在
    # `RECIPES_NEED_UPGRADERS` 是空的, 所以等价于"基础升级卡里去掉速度卡"。

    # 不收速度卡: 本机的推进速率完全由配方自带的温度曲线给出(`ProcessOnce` 不经过
    # `UpgradeControl` 的 `reduce_ticks`), 速度卡一点加速都给不了; 但它同时命中
    # `POWER_POSITIVE`, 会把 `_power_cost_relative` 抬到 1.7, 也就是制冷电费多付 70%。
    # 插进去纯亏, 与其让玩家踩这个坑, 不如不收。

    # 能量卡照收: 制冷机的电费走 `UpgradeControl.ReducePower`, 会被 `_power_cost_relative`
    # 缩放, 所以能量卡确实压得低本机的制冷单价。
    process_item = True
    process_fluid = True
    input_slots = (0,)
    output_slots = (1,)
    fluid_input_slots = {0}
    fluid_output_slots = {1}
    fluid_slot_max_volumes = MAX_FLUID_VOLUMES
    structure_palette = STRUCTURE_PALETTE
    functional_block_ids = {
        ids.IO_ENERGY,
        ids.IO_FLUID1,
        ids.IO_FLUID2,
        ids.IO_ITEM1,
        ids.IO_ITEM2,
    }

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        # 流体吞吐的重入保护标志, 见 transmit_fluids
        self._fluid_io_busy = False
        self._energy_in_ios = []  # type: list[EnergyInputInterface]
        self._fluid_in_ios = []  # type: list[FluidInputInterface]
        self._fluid_out_ios = []  # type: list[FluidOutputInterface]
        self._item_in_ios = []  # type: list[ItemInputInterface]
        self._item_out_ios = []  # type: list[ItemOutputInterface]

    @SuperExecutorMeta.execute_super
    def OnTicking(self):
        # type: () -> None
        pass

    @SuperExecutorMeta.execute_super
    def OnSlotUpdate(self, slot_pos):
        # type: (int) -> None
        if slot_pos in self.output_slots:
            self.try_output_items()
        elif slot_pos in self.input_slots:
            # 输入槽腾出空间后, 物品输入口里没抽完的东西可以再抽一次
            self.try_take_in_items()

    @SuperExecutorMeta.execute_super
    def OnFluidSlotUpdate(self, slot_pos, is_final):
        # type: (int, bool) -> None
        if slot_pos in self.fluid_input_slots or slot_pos in self.fluid_output_slots:
            self.transmit_fluids()

    def UpdateUpgraders(self, upgraders):
        Processor.UpdateUpgraders(self, upgraders)
        self.recipes = Recipes # pyright: ignore[reportAttributeAccessIssue]
        for upgrader, recipes in UpgraderRecipes.items():
            if self.HasUpgrader(upgrader):
                self.recipes = recipes # pyright: ignore[reportAttributeAccessIssue]
                break
        if hasattr(self, "current_recipe"):
            self.recheck_recipe()

    def get_recipe(self):
        # type: () -> tuple[int, MachineRecipeBase | None]
        # 覆写只为顺带把匹配结果同步给客户端: 界面上的配方效率要按"正在跑的那条配方"算,
        # 而温度窗口是配方自带的, 拿错配方读数就是错的。

        # 写在这里而不是逐处调用, 是因为服务端每次确定配方 —— 构造时
        # `ProcessorBase.__init__`、`recheck_recipe`、`start_next` —— 都要先走这里匹配一次,
        # 集中在这一处就不会漏; 没有配方时匹配到 `(0, None)`, 正好写给客户端 -1。

        # 也要覆盖"机器加载后没配方"这一路: 那种情况下别的钩子都不会被调到, 不写的话
        # 客户端会一直读着上次落盘的下标, 机器明明停着却还显示着一个效率读数。
        idx, recipe = Processor.get_recipe(self)
        # 写的是配方在 `ALL_RECIPES` 里的下标, 不是上面那个 `idx` —— 后者是 `self.recipes`
        # 的下标, 而升级后这张表只含一条配方, 与客户端手里的全量表对不上。
        index = -1
        for i, r in enumerate(ALL_RECIPES):
            if r is recipe:
                index = i
                break
        self.bdata[K_RECIPE] = index
        return idx, recipe

    def OnItemInputSlotUpdate(self, slot_pos):
        # type: (int) -> None
        self.try_take_in_items()

    def OnItemOutputSlotUpdate(self, slot_pos):
        # type: (int) -> None
        self.try_output_items()

    def OnFluidInputSlotUpdate(self):
        # type: () -> None
        self.transmit_fluids()

    def OnFluidOutputSlotUpdate(self):
        # type: () -> None
        self.transmit_fluids()

    @SuperExecutorMeta.execute_super
    def OnAddedFluid(self, slot, fluid_id, fluid_volume, is_final):
        # type: (int, str, float, bool) -> None
        # 本机不在这里做额外处理, 保留覆写只是为了把父类实现接进调用链。
        # `Processor.OnAddedFluid` 里"流体到货就重查配方"的逻辑必须真的被执行到: 没有它,
        # 机器一旦因为在输入槽还空着的时候挂上 `DEACTIVE_FLAG_NO_RECIPE`, 之后灌进来的流体
        # 就再也唤不醒它了(见 `OnTicking`: 停机旗挂着时配方循环整个不跑), 而界面搬运又是
        # 被动的, 输入槽灌满后不会再有任何流体变动回调, 于是永久卡死。
        # 之所以不能只靠 `MultiFluidContainer.OnAddedFluid`, 是因为它自己也带着
        # `execute_super`, 按 MRO 排在 `Processor` 前面, 会把 `Processor` 的实现整个挡掉;
        # 所以具体机器必须像 `AirCompressor` / `FluidCondenser` 那样把这两个钩子重声明一遍。
        pass

    @SuperExecutorMeta.execute_super
    def OnReducedFluid(self, slot, fluid_id, reduced_fluid_volume, is_final):
        # type: (int, str, float, bool) -> None
        pass

    def OnStructureChanged(self, ok):
        # type: (bool) -> None
        self.clean()
        if ok:
            self.connect_ios()
        self.CallSync()

    @SuperExecutorMeta.execute_super
    def OnUnload(self):
        self.clean()

    def connect_ios(self):
        # type: () -> None
        self._energy_in_ios = self.GetAllMachines(EnergyInputInterface, ids.IO_ENERGY)
        self._fluid_in_ios = self.GetAllMachines(FluidInputInterface, ids.IO_FLUID1)
        self._fluid_out_ios = self.GetAllMachines(FluidOutputInterface, ids.IO_FLUID2)
        self._item_in_ios = self.GetAllMachines(ItemInputInterface, ids.IO_ITEM1)
        self._item_out_ios = self.GetAllMachines(ItemOutputInterface, ids.IO_ITEM2)
        for machine in self.iter_ios():
            machine.SetMachineRef(self)
        for io in self._item_in_ios:
            io.SetOnSlotUpdateCallback(self.OnItemInputSlotUpdate)
        for io in self._item_out_ios:
            io.SetOnSlotUpdateCallback(self.OnItemOutputSlotUpdate)
        for io in self._fluid_in_ios:
            io.SetOnFluidSlotUpdateCallback(self.OnFluidInputSlotUpdate)
        for io in self._fluid_out_ios:
            io.SetOnFluidSlotUpdateCallback(self.OnFluidOutputSlotUpdate)
        self.try_take_in_items()
        self.try_output_items()
        self.transmit_fluids()

    def iter_ios(self):
        "遍历本机接上的所有接口方块。"
        return (
            machine
            for machines in (
                self._energy_in_ios,
                self._fluid_in_ios,
                self._fluid_out_ios,
                self._item_in_ios,
                self._item_out_ios,
            )
            for machine in machines
        )

    def clean(self):
        # type: () -> None
        for machine in self.iter_ios():
            machine.UnsetMachineRef()
        self._energy_in_ios = []
        self._fluid_in_ios = []
        self._fluid_out_ios = []
        self._item_in_ios = []
        self._item_out_ios = []

    def OnHeatWork(self):
        # type: () -> None
        self.freeze()

    def ProcessOnce(self):
        recipe = self.current_recipe
        if not isinstance(recipe, VacuumFreezerRecipe):
            return False
        # 速率是带符号的: 温度高于配方的 `max_temperature` 时为负, 此时进度倒退, 配方也不
        # 放热(没在推进, 就没有液化热要制冷机搬)。倒退与推进共用同一条温度曲线, 所以温度越
        # 贴近 `max_temperature` 退得越慢, 不会像"超出即清零"那样抖一下就损失整份进度 ——
        # 见 `VacuumFreezerRecipe.GetSignedRateAtKelvin`。
        reduce = recipe.GetSignedRateAtKelvin(self.kelvin)
        if reduce < 0:
            self.ticks_left = min(recipe.max_tick_duration, self.ticks_left - reduce)
        else:
            self.ticks_left = max(0, self.ticks_left - reduce)
            self.heat_value += recipe.tick_heat_value_add * reduce
        if self.ticks_left <= 0:
            self.ticks_left += self.origin_process_ticks
            return True
        else:
            return False

    def freeze(self):
        # type: () -> None
        # 主动降温: 按卡诺制冷机(`Thermal.ActiveCool`)把本机温度压向设定温度。

        # 每个结算周期先按 `MAX_TICK_COOLDOWN_RATE` 的移热速率上限算出本周期想移走
        # 多少热量, 再由 `Thermal` 沿这段温区积分算出耗电。算的是一台接近现实的
        # 制冷机, 而不是可逆的理想机:

        #     - 冷头效率 `COLD_HEAD_EFFICIENCY`(相对理想卡诺)打折
        #     - 蒸发器要有温差 `EVAPORATOR_APPROACH`, 本机温度最多只能逼近它
        #     - 移热速率只决定降温有多快、峰值功率有多高, 不改变总电量

        # 本周期的电能预算是 `min(设定功率 * WORK_INTERVAL, 当前储电)`, 耗电超出
        # 预算时按可负担的比例少移一点热量(同一温度下耗电与移热量成正比)。

        # 本机热容远大于默认值(`CHAMBER_HEAT_CAPACITY`), 所以同样的温度变化要搬走的
        # 热量、以及对应的电费都按热容放大: 从环境温度降到液化温度的总电量在几十万 RF
        # 这个量级。
        if self.kelvin <= self.expected_kelvin:
            return
        budget = min(self.max_power * self.WORK_INTERVAL, self.store_rf)
        if budget <= 0:
            return
        res = Thermal.ActiveCool(
            self.heat_value,
            self.expected_kelvin,
            max_cool=MAX_TICK_COOLDOWN_RATE,
            dt=self.WORK_INTERVAL,
            eta=COLD_HEAD_EFFICIENCY,
            approach=EVAPORATOR_APPROACH,
            capacity=self.heat_capacity,
        )
        Q_removed = res.Q_removed
        energy_used = res.energy_used
        if Q_removed <= 0 or energy_used == float("inf"):
            return
        if energy_used > budget:
            Q_removed *= budget / energy_used
            energy_used = budget
        self.ReducePower(int(round(energy_used)))
        self.heat_value -= Q_removed

    def set_power(self, power):
        # type: (float) -> None
        "设置玩家设定的最大功率, 单位 RF/t。"
        self.max_power = int(min(max(power, 0), MAX_POWER))

    def set_expected_kelvin(self, kelvin):
        # type: (float) -> None
        "设置玩家设定的目标温度, 单位 K。"
        self.bdata[K_EXPECTED_KELVIN] = min(
            max(kelvin, MIN_EXPECTED_KELVIN), MAX_EXPECTED_KELVIN
        )

    @property
    def max_power(self):
        # type: () -> float
        "玩家设定的最大功率, 单位 RF/t; 未设定时为 0(不降温)。"
        return self.bdata[K_MAX_POWER] or 0

    @max_power.setter
    def max_power(self, value):
        # type: (float) -> None
        self.bdata[K_MAX_POWER] = value

    @property
    def expected_kelvin(self):
        # type: () -> float
        "玩家设定的目标温度, 单位 K; 未设定时为环境温度(不降温)。"
        value = self.bdata[K_EXPECTED_KELVIN]
        return MAX_EXPECTED_KELVIN if value is None else value

    def transmit_fluids(self):
        # type: () -> None
        # 流体接口吞吐: 把流体输入口里的流体抽进本机, 再把本机产出的流体送到输出口。

        # 和本机开没开机无关 —— 机器因为缺料/缺电停下来时, 接口照样得能把东西送进来。
        # 结构不完整时(接口方块已不属于本机)直接跳过。

        # 重入保护是必须的: `_on_added_fluid` / `_on_reduced_fluid` 是当场回调
        # `OnFluidSlotUpdate` 的, 而本方法自己就会写接口槽位, 往输出口送流体会立刻
        # 回调回来。没有保护的话, 回调回来时本机产出槽还没扣账, 会被当成还有一整份
        # 流体, 反复往同一个输出口里倒, 凭空多出流体。标志只挡这种重入, 同一帧里被
        # 多个来源各叫一次是照常跑的(重读状态, 幂等)。
        if self._fluid_io_busy or not self.StructureFinished():
            return
        self._fluid_io_busy = True
        try:
            self.try_take_in_fluids()
            self.try_output_fluids()
        finally:
            self._fluid_io_busy = False

    def try_take_in_fluids(self):
        # type: () -> None
        for io in self._fluid_in_ios:
            fluid_id = io.fluid_id
            fluid_volume = io.fluid_volume
            if fluid_id is None or fluid_volume <= 0:
                continue
            _, rest_volume = self.AddFluid(fluid_id, fluid_volume)
            moved_volume = fluid_volume - rest_volume
            if moved_volume <= 0:
                continue
            io.fluid_volume = rest_volume
            io._on_reduced_fluid(fluid_id, moved_volume)

    def try_take_in_items(self):
        # type: () -> None
        for io in self._item_in_ios:
            for slot in io.input_slots:
                item = io.GetSlotItem(slot)
                if item is None:
                    continue
                count_before = item.count
                rest_item = self.PushItem(item)
                if rest_item is None:
                    io.SetSlotItem(slot, None)
                elif rest_item.count < count_before:
                    io.SetSlotItem(slot, rest_item)

    def try_output_fluids(self):
        # type: () -> None
        if not self._fluid_out_ios:
            return
        for slot in self.fluid_output_slots:
            fluid = self.fluids[slot]
            fluid_id = fluid.fluid_id
            if fluid_id is None or fluid.volume <= 0:
                continue
            for io in self._fluid_out_ios:
                if fluid.volume <= 0:
                    break
                if not io.CanAddFluid(fluid_id):
                    continue
                fluid_volume = fluid.volume
                _, rest_volume = io.AddFluid(fluid_id, fluid_volume)
                moved_volume = fluid_volume - rest_volume
                if moved_volume <= 0:
                    continue
                fluid.volume = rest_volume
                self._on_reduced_fluid(slot, fluid_id, moved_volume, True)

    def try_output_items(self):
        # type: () -> None
        if not self._item_out_ios:
            return
        for slot in self.output_slots:
            item = self.GetSlotItem(slot)
            if item is None:
                continue
            count_before = item.count
            for io in self._item_out_ios:
                # 输出口的 IsValidInput 对任何槽位都返回 False, 用不了 PushItem,
                # 改走 OutputItem(底层 PutItemIntoContainer) 直接写容器槽位
                item = io.OutputItem(item)
                if item is None:
                    break
            if item is None:
                self.SetSlotItem(slot, None)
            elif item.count < count_before:
                self.SetSlotItem(slot, item)


@VacuumFreezer.ForOperation(VacuumFreezerSubmitModifiesEvent)
def onSetModifies(event, machine):
    # type: (VacuumFreezerSubmitModifiesEvent, VacuumFreezer) -> None
    power = clamp_power(event.power)
    kelvin = clamp_expected_kelvin(event.kelvin)
    if power is None or kelvin is None:
        return
    machine.set_power(power)
    machine.set_expected_kelvin(kelvin)


