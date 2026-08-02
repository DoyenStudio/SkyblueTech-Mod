# coding=utf-8
from ..define import id_enum, tag_enum
from ..mini_jei.core import RecipesCollection
from ..mini_jei.machinery.mixer import MachineRecipe, MixerRecipe

STORE_RF_MAX = 8800
MAX_FLUID_VOLUME = 2000

_CONCRETE_POWDER_COLORS = (
    "white",
    "orange",
    "magenta",
    "light_blue",
    "yellow",
    "lime",
    "pink",
    "gray",
    "light_gray",
    "cyan",
    "purple",
    "blue",
    "brown",
    "green",
    "red",
    "black",
)


def _concrete_recipe(color):
    # type: (str) -> MixerRecipe
    # 注意: 国服基岩版自定义容器会把各颜色混凝土规范化存储为
    # minecraft:<color>_concrete (例如 aux=0 的 minecraft:concrete 读回为
    # minecraft:white_concrete), 配方输出 id 必须与读回 id 一致, 否则
    # can_output 判定 id 不匹配, 机器每产出一个就 OUTPUT_FULL 停机。
    return MixerRecipe(
        "minecraft:water",
        1000,
        "minecraft:%s_concrete_powder" % color,
        1,
        "minecraft:%s_concrete" % color,
        1,
        tick_duration=50,
        power_cost=30,
    )


recipes = RecipesCollection(
    id_enum.Machinery.MIXER,
    MixerRecipe(
        "minecraft:lava",
        500,
        "minecraft:netherrack",
        1,
        "minecraft:magma",
        1,
        tick_duration=80,
        power_cost=40,
    ),
    MixerRecipe(
        "minecraft:water",
        400,
        id_enum.DUST_BLOCK,
        1,
        "minecraft:clay",
        1,
        tick_duration=40,
        power_cost=30,
    ),
    MixerRecipe(
        id_enum.fluids.CommonGas.COMPRESSED_AIR,
        200,
        id_enum.Dusts.LEAD,
        1,
        id_enum.Dusts.LEAD_OXIDE,
        1,
        tick_duration=60,
        power_cost=35,
    ),
    MixerRecipe(
        id_enum.fluids.Acid.SULFURIC_ACID,
        250,
        id_enum.Dusts.LEAD_OXIDE,
        1,
        id_enum.Dusts.LEAD_SULFATE,
        1,
        tick_duration=50,
        power_cost=30,
    ),
)  # type: RecipesCollection[MachineRecipe]

for color in _CONCRETE_POWDER_COLORS:
    recipes.add_recipe(_concrete_recipe(color))
