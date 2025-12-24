# coding=utf-8
#
from mod.server.blockEntityData import BlockEntityData
from skybluetech_scripts.tooldelta.events.basic import CustomS2CEvent, CustomC2SEvent
from skybluetech_scripts.tooldelta.internal import ClientComp, ClientLevelId
from skybluetech_scripts.tooldelta.general import ClientInitCallback, ServerInitCallback
from skybluetech_scripts.tooldelta.api.timer import AsTimerFunc
from skybluetech_scripts.tooldelta.no_runtime_typing import TYPE_CHECKING
from skybluetech_scripts.tooldelta.events.client.block import ModBlockEntityLoadedClientEvent, ModBlockEntityRemoveClientEvent
from .basic import BaseMachine, RegisterMachine

# TYPE_CHECKING
if TYPE_CHECKING:
    from mod.client.component.drawingShapeCompClient import DrawingShapeCompClient
# TYPE_CHECKING END

INFINITY = float("inf")


@RegisterMachine
class CreativePowerAcceptor(BaseMachine):
    block_name = "skybluetech:creative_power_acceptor"
    store_rf_max = 0

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        BaseMachine.__init__(self, dim, x, y, z, block_entity_data)
        lastUpdatePool[(self.dim, self.x, self.y, self.z)] = -2
        updatePool[(self.dim, self.x, self.y, self.z)] = 0
        self.power = 0
        self.delay = 20

    def AddPower(self, rf, is_generator=False, max_limit=None, depth=0):
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

    def OnUnload(self):
        self.active = False
        del updatePool[(self.dim, self.x, self.y, self.z)]
        del lastUpdatePool[(self.dim, self.x, self.y, self.z)]


updatePool = {} # type: dict[tuple[int, int, int, int], int]
lastUpdatePool = {} # type: dict[tuple[int, int, int, int], int]
cTextPool = {} # type: dict[tuple[int, tuple[float, float, float]], DrawingShapeCompClient]


class CreativePowerAcceptorPowerUpdateRequest(CustomC2SEvent):
    name = "st:CPAPUpdateRequest"

    def __init__(self, dim=-1, x=0, y=0, z=0):
        self.dim = dim
        self.x = x
        self.y = y
        self.z = z

    def marshal(self):
        return {
            "dim": self.dim,
            "x": self.x,
            "y": self.y,
            "z": self.z,
        }

    def unmarshal(self, data):
        self.dim = data["dim"]
        self.x = data["x"]
        self.y = data["y"]
        self.z = data["z"]
        self.mId = data["__id__"]
        pass



class CreativePowerAcceptorPowerUpdate(CustomS2CEvent):
    name = "st:CPAPUpdate"

    def __init__(self, datas=None):
        # type: (list[list[int]] | None) -> None
        self.datas = datas or []

    def marshal(self):
        return self.datas

    def unmarshal(self, data):
        # type: (list[list[int]]) -> None
        self.datas = data


def addText(dim, pos, default_text=""):
    # type: (int, tuple[int, int, int], str) -> None
    x, y, z = pos
    tx = x + 0.5
    ty = y + 1.1
    tz = z + 0.5
    t = ClientComp.CreateDrawing(ClientLevelId).AddTextShape((tx, ty, tz), default_text)
    cTextPool[(dim, pos)] = t

def removeText(dim, pos):
    # type: (int, tuple[int, int, int]) -> None
    cTextPool.pop((dim, pos)).Remove()

def updateText(dim, pos, text):
    # type: (int, tuple[int, int, int], str) -> None
    text_elem = cTextPool.get((dim, pos), None)
    if text_elem is not None:
        text_elem.SetText(text)

@ModBlockEntityLoadedClientEvent.Listen()
def onModBlockLoaded(event):
    # type: (ModBlockEntityLoadedClientEvent) -> None
    if event.blockName == CreativePowerAcceptor.block_name:
        addText(event.dimensionId, (event.posX, event.posY, event.posZ), "输入功率： --")
        CreativePowerAcceptorPowerUpdateRequest(
            event.dimensionId, event.posX, event.posY, event.posZ
        ).send()

@ModBlockEntityRemoveClientEvent.Listen()
def onModBlockRemoved(event):
    # type: (ModBlockEntityRemoveClientEvent) -> None
    if event.blockName == CreativePowerAcceptor.block_name:
        removeText(event.dimensionId, (event.posX, event.posY, event.posZ))

@CreativePowerAcceptorPowerUpdate.Listen()
def onPowerUpdate(event):
    # type: (CreativePowerAcceptorPowerUpdate) -> None
    for dim, x, y, z, power in event.datas:
        if power == -1:
            text = "输入功率： §a无限 RF/t"
        else:
            text = "输入功率： §a%d RF/t" % power
        updateText(dim, (x, y, z), text)

@CreativePowerAcceptorPowerUpdateRequest.Listen()
def onPowerUpdateRequest(event):
    # type: (CreativePowerAcceptorPowerUpdateRequest) -> None
    dim = event.dim
    x = event.x
    y = event.y
    z = event.z
    if dim == -1:
        # TODO: 客户端可能恶意连续请求以占用过多网络资源
        CreativePowerAcceptorPowerUpdate(
            [list(k) + [v] for k, v in updatePool.items()]
        ).send(event.mId)
    else:
        CreativePowerAcceptorPowerUpdate(
            [[dim, x, y, z, updatePool.get((dim, x, y, z), -32768)]]
        ).send(event.mId)

@ClientInitCallback()
def onClientInit():
    CreativePowerAcceptorPowerUpdateRequest().send()

@ServerInitCallback()
@AsTimerFunc(1)
def onRepeatUpdate():
    compared = [list(k) + [v] for k, v in updatePool.items()][:50] # NOTE: 全局至多同时有 50 个功率更新
    if compared:
        CreativePowerAcceptorPowerUpdate(compared).sendAll()
