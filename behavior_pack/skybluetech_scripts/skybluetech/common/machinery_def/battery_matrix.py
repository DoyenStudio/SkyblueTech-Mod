# coding=utf-8
from ..define.id_enum import BatteryMatrix
from ..utils.structure_palette import GenerateSimpleStructureTemplate

K_STORE_RF = "st:total_store_rf"
K_RF_MAX = "st:total_rf_max"
K_ENABLE_INPUT = "st:enable_input"
K_ENABLE_OUTPUT = "st:enable_output"

K_INPUT_POWER = "st:input_power"
K_OUTPUT_POWER = "st:output_power"

CORE = BatteryMatrix.CORE
FRAME = BatteryMatrix.FRAME
IO_ENERGY_INPUT = BatteryMatrix.IO_ENERGY_INPUT
IO_ENERGY_OUTPUT = BatteryMatrix.IO_ENERGY_OUTPUT

STRUCTURE_PATTERN_MAPPING = {
    "F": FRAME,
    "f": [FRAME, IO_ENERGY_INPUT, IO_ENERGY_OUTPUT],
    "C": CORE,
}
STRUCTURE_PATTERN = {
    -1: [
        "FfF",
        "fff",
        "FfF",
    ],
    0: [
        "f#f",
        "fCf",
        "fff",
    ],
    1: [
        "FfF",
        "fff",
        "FfF",
    ],
}
# 这里是"不少于"而不是"恰好": 输入/输出接口在 'f' 位上想放几个就放几个, 放得越多
# 电池仓的充放电吞吐越高(每个接口各自独立走一遍 BatteryMatrix.AddPower / TakeoutPower)。
STRUCTURE_REQUIRE_BLOCKS = {
    IO_ENERGY_INPUT: 1,
    IO_ENERGY_OUTPUT: 1,
    CORE: 1,
}
STRUCTURE_PALETTE = GenerateSimpleStructureTemplate(
    STRUCTURE_PATTERN_MAPPING,
    STRUCTURE_PATTERN,
    require_blocks_count=STRUCTURE_REQUIRE_BLOCKS,
)
