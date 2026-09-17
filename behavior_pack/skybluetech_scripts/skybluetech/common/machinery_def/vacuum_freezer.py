# coding=utf-8
import math

from ..define.id_enum import Machinery, Upgraders, VacuumFreezer, fluids
from ..mini_jei.core import RecipesCollection
from ..mini_jei.machinery.vacuum_freezer import (
    Input,
    Output,
    VacuumFreezerRecipe,
)
from ..utils.structure_palette import GenerateSimpleStructureTemplate

STORE_RF_MAX = 80000
MAX_FLUID_VOLUMES = (4000, 4000)

K_MAX_POWER = "st:max_power"
K_EXPECTED_KELVIN = "st:expected_kelvin"
K_RECIPE = "st:recipe"
# 服务端同步给客户端的"当前配方下标", 索引 ALL_RECIPES; 没有配方在跑时为 -1。
# 客户端拿它算"配方效率"读数。
MAX_POWER = STORE_RF_MAX
MIN_EXPECTED_KELVIN = 6.0
# 可设定的最低目标温度, 单位 K
# 下限由蒸发器温差 `EVAPORATOR_APPROACH` 决定: 冷头要比被冷却物更冷才能吸热, 所以
# 本机温度最多只能逼近 `EVAPORATOR_APPROACH`(5K), 取它再加 1K 当余量。设得更低的话
# 机器永远到不了目标, 只会一直满功率空转。
MAX_EXPECTED_KELVIN = 300.0
# 可设定的最高目标温度, 单位 K; 即环境温度, 此时机器不降温
CHAMBER_HEAT_CAPACITY = 500.0
# 冷却仓的热容, 单位 RF/K。

# 仓里装的是待降温的空气和物料, 把它当成一大团热容很高的物质: 温度每降 1K 都要
# 搬走 `CHAMBER_HEAT_CAPACITY` 的 RF, 于是从环境温度降到液化温度总共要几十万 RF。

# 这个值只影响本机: `HeatCtrl.heat_capacity` 是按机器覆写的, 全局的
# `Thermal.HEAT_CAPACITY` 保持 1.0 RF/K, 其他热机一点都不受影响。

MAX_TICK_COOLDOWN_RATE = CHAMBER_HEAT_CAPACITY
# "主动降温的移热速率上限, 单位 RF/t。

# 取默认热容的 1 倍(即等于 `CHAMBER_HEAT_CAPACITY`)时, 每个结算周期最多搬走相当于
# 5K 的热量, 降温速度与热容无关, 恒定 5K/周期; 想让降温更快或更慢, 就改这个比值。

# 移热速率是机器本身的泵送能力, 与玩家设定的功率无关。它只决定降温有多快、
# 峰值功率有多高, 不改变降完一段温区要花的总电量(`Thermal.ActiveCool` 沿
# 温区积分计费, 与步长无关)。


COLD_HEAD_EFFICIENCY = 0.3
# "冷头效率, 相对理想卡诺制冷机, 取值 (0, 1]。

# 真实的斯特林制冷机大约只有 0.2~0.3 倍卡诺, 脉管机更低; 取 1.0 就是理想可逆机。

# 它与 `EVAPORATOR_APPROACH` 一起决定本机的制冷单价曲线(见 `Thermal.CoolCOP`): 在全局
# 制冷参照温度 `Thermal.COOL_REFERENCE_KELVIN`(80K)上, 本机的 COP 恰好等于
# `Thermal.COOL_REFERENCE_COP`(= 1 / `Thermal.ELECTRIC_PER_HEAT`, 即 0.1), 也就是搬走
# 1 RF 热量与加热 1 RF 热量同价。这两个常数不要单独改: 动任何一个都会偏离全包的参照点。

EVAPORATOR_APPROACH = 5.0
# "蒸发器温差, 单位 K。

# 冷头必须比被冷却物更冷才能吸热, 所以本机温度最多只能逼近这个温差。温差越大
# 越费电(同样一份热量要多花 (T_h - T_c) / T_c 的功), 能到的温度也越高。取 0
# 相当于直接拿被冷却物的温度当蒸发温度, 是最乐观的估计。

ALL_RECIPES = [
    VacuumFreezerRecipe(
        input_fluid=Input(fluids.CommonGas.COMPRESSED_AIR, 16),
        output_fluid=Output(fluids.CommonLiquid.LIQUID_AIR, 1),
        max_temperature=100,
        fit_temperature=80,
        max_tick_duration=8,
        tick_heat_value_add=40,
        # 液化配方每 tick 释放进仓里的热量, 单位 RF/t。
        # 压缩空气液化会放热, 这份热量要由制冷机搬走。80K 正是全包的制冷参照温度
        # (`Thermal.COOL_REFERENCE_KELVIN`): 本机在这里的 COP 等于 `Thermal.COOL_REFERENCE_COP`
        # = 0.1, 单价等于加热侧的 `Thermal.ELECTRIC_PER_HEAT` = 10 RF电/RF热, 于是制冷机
        # 要花约 400 RF/t 的电, 正好是本机设计工况下该有的量级。
        # 每份配方释放的总热量是 `LIQUEFY_TICK_HEAT_VALUE_ADD * LIQUEFY_MIN_TICKS` = 320 RF,
        # 对应的制冷耗电约 3200 RF(1 mB 液态空气)。
    ),
    VacuumFreezerRecipe(
        input_fluid=Input(fluids.Vanilla.WATER, 1000),
        output_item=Output("minecraft:ice", 1),
        max_temperature=273,
        fit_temperature=265,
        max_tick_duration=8,
        tick_heat_value_add=20,
    ),
    VacuumFreezerRecipe(
        input_fluid=Input(fluids.CommonGas.COMPRESSED_AIR, 24),
        output_fluid=Output(fluids.CommonGas.NITROGEN, 1),
        max_temperature=78,
        fit_temperature=75,
        max_tick_duration=10,
        tick_heat_value_add=2,
        extra_upgrader_id=Upgraders.SPEC_NITROGEN_EXTRACTION,
    ),
]

RECIPES_NOT_NEED_UPGRADERS = [
    recipe for recipe in ALL_RECIPES if recipe.extra_upgrader_id is None
]
RECIPES_NEED_UPGRADERS = [
    (recipe.extra_upgrader_id, recipe)
    for recipe in ALL_RECIPES
    if recipe.extra_upgrader_id is not None
]

recipes = RecipesCollection(Machinery.VACUUM_FREEZER, *RECIPES_NOT_NEED_UPGRADERS)
# 本机的默认配方组, 即所有不需要升级卡的配方。

upgrader_recipes = {
    upgrader: RecipesCollection(Machinery.VACUUM_FREEZER + "." + upgrader, recipe)
    for upgrader, recipe in RECIPES_NEED_UPGRADERS
}
# 需要升级卡的配方各自预建一个只含它自己的配方组, 键是升级卡 id。

# 与 MagmaFurnace 的差别: 那边装卡是"特化成另一套配方表"(另一套配方与基础配方并存),
# 本机装卡后是"只跑这一条配方", 基础配方全部停用, 所以每个组里只放一条。

# 在模块级预建而不是在机器的 `UpdateUpgraders` 里现建: 那里每次升级槽变动都会 new 一个
# 同名配方组, 而 `RecipesCollection.__init__` 会重跑一遍 `RegisterRecipe` 并把
# `_registered_collections[Machinery.VACUUM_FREEZER]` 覆盖成最后被碰过的那个实例。

all_recipes = RecipesCollection(Machinery.VACUUM_FREEZER + ".all", *ALL_RECIPES)
# 全量配方组, 只给客户端的配方页用: 那一页要把需要升级卡的配方也列出来(渲染器会在
# 配方上标"需要机器升级"), 而机器实际在跑的配方表是 `recipes` 或 `upgrader_recipes`。


STRUCTURE_PALETTE = GenerateSimpleStructureTemplate(
    {
        "A": VacuumFreezer.FRAME,
        "B": VacuumFreezer.CONDENSER,
        "C": [
            VacuumFreezer.FRAME,
            VacuumFreezer.IO_ENERGY,
            VacuumFreezer.IO_FLUID1,
            VacuumFreezer.IO_ITEM1,
        ],
        "D": [VacuumFreezer.FRAME, VacuumFreezer.IO_ENERGY],
        "E": [
            VacuumFreezer.FRAME,
            VacuumFreezer.IO_FLUID2,
            VacuumFreezer.IO_ITEM2,
        ],
    },
    {
        -1: [
            "DCD",
            "CAC",
            "DCD",
        ],
        0: [
            "A#A",
            "A.A",
            "AAA",
        ],
        1: [
            "AEA",
            "E.E",
            "AEA",
        ],
        2: [
            "BBB",
            "BBB",
            "BBB",
        ],
    },
    require_blocks_count={
        VacuumFreezer.IO_ENERGY: 1,
    },
)


def _num_check(value):
    # type: (object) -> float | None
    if not isinstance(value, (int, float)):
        return None
    return None if (math.isinf(value) or math.isnan(value)) else value


def clamp_power(value):
    # type: (object) -> int | None
    value = _num_check(value)
    if value is None:
        return None
    return int(min(max(value, 0.0), MAX_POWER))


def clamp_expected_kelvin(value):
    # type: (object) -> float | None
    value = _num_check(value)
    if value is None:
        return None
    return min(max(value, MIN_EXPECTED_KELVIN), MAX_EXPECTED_KELVIN)
