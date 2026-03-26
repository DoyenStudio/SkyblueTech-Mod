# coding=utf-8
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ...common.define.id_enum.machinery import CREATIVE_POWER_ACCEPTOR as MACHINE_ID
from ...common.machinery_def.creative_power_acceptor import K_POWER
from .basic import BaseMachine, RegisterMachine


@RegisterMachine
class CreativePowerAcceptor(BaseMachine):
    block_name = MACHINE_ID
    store_rf_max = 0

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        BaseMachine.__init__(self, dim, x, y, z, block_entity_data)
        self.power = 0
        self.delay = 20
        self.bdata[K_POWER] = 0

    def AddPower(self, rf):
        self.power += rf
        return True, 0

    def OnTicking(self):
        self.delay -= 1
        if self.delay <= 0:
            # 我没招了, 方块 ticking 不均匀。。。取平均值吧
            self.bdata[K_POWER] = self.power // 20
            self.power = 0
            self.delay = 20

    @SuperExecutorMeta.execute_super
    def OnUnload(self):
        pass
