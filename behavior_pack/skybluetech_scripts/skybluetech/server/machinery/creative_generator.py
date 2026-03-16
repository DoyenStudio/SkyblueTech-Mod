# coding=utf-8
#
from mod.server.blockEntityData import BlockEntityData
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ...common.define.id_enum.machinery import CREATIVE_GENERATOR as MACHINE_ID
from .basic import BaseGenerator, RegisterMachine

INFINITY = float("inf")  # type: int # type: ignore


@RegisterMachine
class CreativeGenerator(BaseGenerator):
    block_name = MACHINE_ID
    store_rf_max = 0
    energy_io_mode = (1, 1, 1, 1, 1, 1)

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        self.active = True
        self.update_counter = 0

    def OnTicking(self):
        # 由于充能值使用 Infinity 导致 AddPower 总是检测到能量值没有变动
        # 所以不作 active 优化
        self.GeneratePower(INFINITY)

    def OnTryActivate(self):
        # type: () -> None
        self.active = True
        self.update_counter = 0

    def OnUnload(self):
        self.active = False
