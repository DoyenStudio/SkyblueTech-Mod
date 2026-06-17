# coding=utf-8
from ..define.id_enum import fluids

K_DIGGING_POS = "st:digging_pos"
K_WORK_MODE = "st:work_mode"
USE_FLUID = fluids.CommonOil.LUBRICANT
VOLUME_COST_ONCE = 5
STORE_RF_MAX = 10000
MAX_FLUID_VOLUME = 2000


class WorkMode:
    UNKNOWN = -1
    WORKING = 0
    FLUID_LACK = 1
    POWER_LACK = 2
    FINISHED = 3
    OUTPUT_FULL = 4
    FAST_SKIP = 5
    OTHER = 127

    @classmethod
    def zh_cn(cls, mode):
        # type: (int) -> str
        return {
            cls.WORKING: "§a工作中",
            cls.FLUID_LACK: "§6润滑油不足",
            cls.POWER_LACK: "§c能量不足",
            cls.FINISHED: "§a已完成",
            cls.OUTPUT_FULL: "§c输出槽已满",
            cls.FAST_SKIP: "§e快进中",
            cls.OTHER: "§7已停机",
        }.get(mode, "未知状态")


BLOCK_CAN_MINE = {
    "minecraft:stone",
    "minecraft:deepslate",
    "minecraft:andesite",
    "minecraft:granite",
    "minecraft:diorite",
    "minecraft:tuff",
}
