# coding=utf-8
#
from mod.server.blockEntityData import BlockEntityData
from .basic import BaseMachine, RegisterMachine

INFINITY = float("inf")


@RegisterMachine
class CreativeGenerator(BaseMachine):
    block_name = "skybluetech:creative_generator"
    store_rf_max = 0
    energy_io_mode = (1, 1, 1, 1, 1, 1)

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        BaseMachine.__init__(self, dim, x, y, z, block_entity_data)
        self.active = True
        self.update_counter = 0

    def OnTicking(self):
        # 由于充能值使用 Infinity 导致 AddPower 总是检测到能量值没有变动
        # 所以不作 active 优化
        self.AddPower(INFINITY, True) # type: ignore

    def OnTryActivate(self):
        # type: () -> None
        self.active = True
        self.update_counter = 0

    def OnUnload(self):
        self.active = False
