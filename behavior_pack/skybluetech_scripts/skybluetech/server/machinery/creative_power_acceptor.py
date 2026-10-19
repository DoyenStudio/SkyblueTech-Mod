# coding=utf-8

from ...common.define.id_enum import Machinery
from ...common.machinery_def.creative_power_acceptor import K_POWER
from .basic import BaseMachine
from .core import RegisterMachine


@RegisterMachine
class CreativePowerAcceptor(BaseMachine):
    block_name = Machinery.CREATIVE_POWER_ACCEPTOR
    store_rf_max = 0

    def __init__(self, dim, x, y, z, block_entity_data):
        super(CreativePowerAcceptor, self).__init__(dim, x, y, z, block_entity_data)
        self.power = 0
        self.delay = 20
        self.bdata[K_POWER] = 0
        self.handler.SubscribeOnTicking(self._creative_power_acceptor_on_ticking)

    def AddPower(self, rf):
        self.power += rf
        return True, 0

    def _creative_power_acceptor_on_ticking(self):
        self.delay -= 1
        if self.delay <= 0:
            # 我没招了, 方块 ticking 不均匀。。。取平均值吧
            # 不要去掉 int, 不然有神秘 bug 导致无法保存 nbt
            self.bdata[K_POWER] = int(self.power // 20)
            self.power = 0
            self.delay = 20
