# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.id_enum import DistillationColumn, fluids
from skybluetech_scripts.skybluetech.common.mini_jei.core import RecipesCollection
from skybluetech_scripts.skybluetech.common.mini_jei.machinery.distillation_column import (
    DistillationColumnRecipe, DistillationFraction,
)
from skybluetech_scripts.skybluetech.common.utils.structure_palette import (
    GenerateSimpleStructureTemplate,
    StructureBlockPalette,
)

INPUT_MAX_VOLUME = 12000
MAX_OUTPUT_PORTS = 4
MIN_OUTPUT_PORTS = 2
# 沿用小型蒸馏仓的起始热容，避免汽化扣热造成剧烈温度跳变。
CHAMBER_HEAT_CAPACITY = 50.0
MIN_DISPLAY_TEMPERATURE = 300.0
MAX_DISPLAY_TEMPERATURE = 900.0
K_OUTPUT_CAPACITY = "st:column_output_capacity"
K_OUTPUT_COUNT = "st:column_output_count"

# 同一输入的重叠温区按声明顺序选择第一条；具体配方在此添加。
recipes = RecipesCollection(
    DistillationColumn.CONTROLLER,
    DistillationColumnRecipe(
        fluids.CommonLiquid.LIQUID_RESIN, 244, 450, 500, 600, 1.0,
        [DistillationFraction(fluids.CommonOil.TREE_OIL, 100.0 / 244.0, 400, 450, 4.0)],
        fluids.Molten.ROSIN, tick_duration=200,
    ),
)

FRAME = DistillationColumn.FRAME
IO_HEAT = DistillationColumn.IO_HEAT
IO_FLUID1 = DistillationColumn.IO_FLUID1
IO_FLUID2 = DistillationColumn.IO_FLUID2

# 区分 O 与 o, f 与 H、I:
# 在自动建造结构时尽可能显式只放置 1 个液体输入口和受热口、3 个液体输出口
STRUCTURE_PALETTE_DICT = {
    -1: ["FfffF", "fFFFf", "fFfFH", "fFFFf", "FfIfF"],
    0: ["Ff#fF", "f...f", "o...o", "f...f", "FfofF"],
    1: ["FFoFF", "F...F", "o...o", "F...F", "FFOFF"],
    2: ["FFoFF", "F...F", "o...o", "F...F", "FFOFF"],
    3: ["FFoFF", "F...F", "o...o", "F...F", "FFOFF"],
    4: ["FFoFF", "F...F", "o...o", "F...F", "FFoFF"],
    5: ["FFFFF", "FFFFF", "FFOFF", "FFFFF", "FFFFF"],
}

STRUCTURE_KEYS = {
    "F": FRAME,
    "f": [FRAME, IO_HEAT, IO_FLUID1],
    "H": [IO_HEAT, FRAME],
    "I": [IO_FLUID1, FRAME],
    "O": [IO_FLUID2, FRAME],
    "o": [FRAME, IO_FLUID2],
}
STRUCTURE_REQUIRE_BLOCKS = {IO_FLUID2: MIN_OUTPUT_PORTS, IO_HEAT: 1, IO_FLUID1: 1}
STRUCTURE_PALETTE = GenerateSimpleStructureTemplate(
    STRUCTURE_KEYS,
    STRUCTURE_PALETTE_DICT,
    "#",
    require_blocks_count=STRUCTURE_REQUIRE_BLOCKS,
)
