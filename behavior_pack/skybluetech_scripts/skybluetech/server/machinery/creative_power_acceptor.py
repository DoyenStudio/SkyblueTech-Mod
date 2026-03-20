# coding=utf-8
from skybluetech_scripts.tooldelta.general import ServerInitCallback
from skybluetech_scripts.tooldelta.api.common import AsTimerFunc
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ...common.events.machinery.creative_power_acceptor import (
    CreativePowerAcceptorPowerUpdate,
    CreativePowerAcceptorPowerUpdateRequest,
)
from ...common.define.id_enum.machinery import CREATIVE_POWER_ACCEPTOR as MACHINE_ID
from .basic import BaseMachine, RegisterMachine


INFINITY = float("inf")


@RegisterMachine
class CreativePowerAcceptor(BaseMachine):
    block_name = MACHINE_ID
    store_rf_max = 0

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        BaseMachine.__init__(self, dim, x, y, z, block_entity_data)
        lastUpdatePool[(self.dim, self.x, self.y, self.z)] = -2
        updatePool[(self.dim, self.x, self.y, self.z)] = 0
        self.power = 0
        self.delay = 20

    def AddPower(self, rf, max_limit=None, depth=0):
        if max_limit is not None:
            rf = min(rf, max_limit)
        self.power += rf
        return True, 0

    def OnTicking(self):
        if self.power == INFINITY:
            self.power = -1
        self.delay -= 1
        if self.delay <= 0:
            # 我没招了, 方块 ticking 不均匀。。。取平均值吧呵呵呵呵呵呵
            updatePool[(self.dim, self.x, self.y, self.z)] = self.power // 20
            self.power = 0
            self.delay = 20

    @SuperExecutorMeta.execute_super
    def OnUnload(self):
        self.active = False
        del updatePool[(self.dim, self.x, self.y, self.z)]
        del lastUpdatePool[(self.dim, self.x, self.y, self.z)]


updatePool = {}  # type: dict[tuple[int, int, int, int], int]
lastUpdatePool = {}  # type: dict[tuple[int, int, int, int], int]


@CreativePowerAcceptorPowerUpdateRequest.Listen()
def onPowerUpdateRequest(event):
    # type: (CreativePowerAcceptorPowerUpdateRequest) -> None
    dim = event.dim
    x = event.x
    y = event.y
    z = event.z
    if dim == -1:
        # TODO: 客户端可能恶意连续请求以占用过多网络资源
        CreativePowerAcceptorPowerUpdate([
            list(k) + [v] for k, v in updatePool.items()
        ]).send(event.player_id)
    else:
        CreativePowerAcceptorPowerUpdate([
            [dim, x, y, z, updatePool.get((dim, x, y, z), -32768)]
        ]).send(event.player_id)


@ServerInitCallback()
@AsTimerFunc(1)
def onRepeatUpdate():
    compared = [list(k) + [v] for k, v in updatePool.items()][
        :50
    ]  # NOTE: 全局至多同时有 50 个功率更新
    if compared:
        CreativePowerAcceptorPowerUpdate(compared).sendAll()
