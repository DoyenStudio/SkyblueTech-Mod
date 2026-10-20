# coding=utf-8
"""机器共享常量和流体槽数据类型；两端可导入。"""
from ..machinery_def.basic import (
    K_STORE_RF, K_DEACTIVE_FLAGS, K_TICKS_LEFT, K_PROGRESS, K_HEAT_VALUE,
    K_DESTROY_FLAG, K_STRUCTURE_LACKED_BLOCKS, K_STRUCTURE_LACKED_BLOCK_POSES,
    FluidSlotClient, FluidSlotServer,
)
from ..define.id_enum.utils import SimpleEnum
from ..define import flags
from ..define.id_enum import Upgraders
from ..utils.phys_math import Thermal
from ..utils.structure_palette import StructureBlockPalette, GenerateSimpleStructureTemplate

__all__ = [
    "K_STORE_RF", "K_DEACTIVE_FLAGS", "K_TICKS_LEFT", "K_PROGRESS", "K_HEAT_VALUE",
    "K_DESTROY_FLAG", "K_STRUCTURE_LACKED_BLOCKS", "K_STRUCTURE_LACKED_BLOCK_POSES",
    "FluidSlotClient", "FluidSlotServer", "SimpleEnum",
    "flags", "Upgraders", "Thermal", "StructureBlockPalette", "GenerateSimpleStructureTemplate",
]
