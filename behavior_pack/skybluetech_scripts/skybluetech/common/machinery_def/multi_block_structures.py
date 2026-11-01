# coding=utf-8
"""多方块控制器 ID 到未旋转结构调色板的公共表。"""
from skybluetech_scripts.skybluetech.common.define.id_enum.multi_block_structure import (
    BatteryMatrix,
    BedrockLavaDrill,
    BrineEvaporationPond,
    Fermenter,
    SeawaterReservoir,
    VacuumFreezer,
)
from skybluetech_scripts.skybluetech.common.machinery_def.battery_matrix import (
    STRUCTURE_PALETTE as BATTERY_MATRIX_PALETTE,
)
from skybluetech_scripts.skybluetech.common.machinery_def.bedrock_lava_drill import (
    STRUCTURE_PALETTE as BEDROCK_LAVA_DRILL_PALETTE,
)
from skybluetech_scripts.skybluetech.common.machinery_def.brine_evaporation_pond import (
    STRUCTURE_PALETTE as BRINE_EVAPORATION_POND_PALETTE,
)
from skybluetech_scripts.skybluetech.common.machinery_def.fermenter import (
    STRUCTURE_PALETTE as FERMENTER_PALETTE,
)
from skybluetech_scripts.skybluetech.common.machinery_def.seawater_pump import (
    STRUCTURE_PALETTE as SEAWATER_RESERVOIR_PALETTE,
)
from skybluetech_scripts.skybluetech.common.machinery_def.vacuum_freezer import (
    STRUCTURE_PALETTE as VACUUM_FREEZER_PALETTE,
)


# 调色板以朝北的控制器为基准，使用时根据控制器朝向旋转副本。
CONTROLLER_STRUCTURE_PALETTES = {
    BatteryMatrix.CONTROLLER: BATTERY_MATRIX_PALETTE,
    BedrockLavaDrill.CONTROLLER: BEDROCK_LAVA_DRILL_PALETTE,
    BrineEvaporationPond.CONTROLLER: BRINE_EVAPORATION_POND_PALETTE,
    Fermenter.CONTROLLER: FERMENTER_PALETTE,
    SeawaterReservoir.CONTROLLER: SEAWATER_RESERVOIR_PALETTE,
    VacuumFreezer.CONTROLLER: VACUUM_FREEZER_PALETTE,
}
