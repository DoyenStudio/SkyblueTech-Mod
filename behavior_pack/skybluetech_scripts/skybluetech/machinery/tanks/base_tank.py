# coding=utf-8
#
from mod.server.blockEntityData import BlockEntityData
from skybluetech_scripts.tooldelta.general import ClientInitCallback
from skybluetech_scripts.tooldelta.api.timer import AsTimerFunc
from skybluetech_scripts.tooldelta.api.server import (
    UpdateBlockStates,
    GetBlockTags,
    GetBlockName,
)
from skybluetech_scripts.tooldelta.api.client.block import GetBlockEntityData
from skybluetech_scripts.tooldelta.events.server import BlockNeighborChangedServerEvent
from skybluetech_scripts.tooldelta.events.client import (
    ModBlockEntityLoadedClientEvent,
    ModBlockEntityRemoveClientEvent,
)
from ...ui_sync.machines.general_tank import GeneralTankUISync
from ...utils.fluid_model import FluidModel
from ...utils.constants import DXYZ_FACING, FACING_EN
from ...transmitters.pipe.logic import isPipe
from ..basic import BaseMachine, FluidContainer, GUIControl
from ..basic.fluid_container import K_FLUID_ID, K_FLUID_VOLUME

INFINITY = float("inf")
registered_tanks = {} # type: dict[str, type[BasicTank]]


class BasicTank(BaseMachine, FluidContainer, GUIControl):
    is_non_energy_machine = True
    fluid_io_mode = (-1, -1, -1, -1, -1, -1)
    fluid_io_fix_mode = 0
    max_fluid_volume = 0

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        BaseMachine.__init__(self, dim, x, y, z, block_entity_data)
        FluidContainer.__init__(self, dim, x, y, z, block_entity_data)
        self.sync = GeneralTankUISync.NewServer(self).Activate()
        self.OnSync()

    def OnSync(self):
        self.sync.fluid_id = self.fluid_id
        self.sync.fluid_volume = self.fluid_volume
        self.sync.max_volume = self.max_fluid_volume
        self.sync.MarkedAsChanged()

    def Dump(self):
        FluidContainer.Dump(self)

    # RENDER

    def OnPlaced(self, _):
        for dx, dy, dz in DXYZ_FACING.keys():
            facing_en = FACING_EN[DXYZ_FACING[dx, dy, dz]]
            bname = GetBlockName(self.dim, (self.x + dx, self.y + dy, self.z + dz))
            if not bname:
                continue
            connectToWire = isPipe(bname)
            UpdateBlockStates(
                self.dim,
                (self.x, self.y, self.z),
                {"skybluetech:connection_" + facing_en: connectToWire},
            )

    def OnNeighborChanged(self, event):
        # type: (BlockNeighborChangedServerEvent) -> None
        dx = event.neighborPosX - self.x
        dy = event.neighborPosY - self.y
        dz = event.neighborPosZ - self.z
        facing_en = FACING_EN[DXYZ_FACING[dx, dy, dz]]
        connectToWire = isPipe(event.toBlockName)
        UpdateBlockStates(
            self.dim,
            (self.x, self.y, self.z),
            {"skybluetech:connection_" + facing_en: connectToWire},
        )


def RegisterTank(tank_class):
    # type: (type[BasicTank]) -> type[BasicTank]
    registered_tanks[tank_class.block_name] = tank_class
    return tank_class


# CLIENT PARTS


client_tank_datas = {} # type: dict[tuple[int, int, int], tuple[type[BasicTank], str | None, float]]
client_models = {} # type: dict[tuple[int, int, int], tuple[type[BasicTank], FluidModel]]


@ModBlockEntityLoadedClientEvent.Listen()
def onModBlockEntityLoadedClientEvent(event):
    # type: (ModBlockEntityLoadedClientEvent) -> None
    x = event.posX
    y = event.posY
    z = event.posZ
    tank_cls = registered_tanks.get(event.blockName, None)
    if tank_cls is None:
        return
    blockEntityData = GetBlockEntityData(x, y, z)
    if blockEntityData is None:
        raise Exception("BlockEntityData is None")
    fluid_id, fluid_vol = getFluidDataFromBlock(blockEntityData)
    client_tank_datas[(x, y, z)] = (tank_cls, fluid_id, fluid_vol)
    if fluid_id is not None:
        loadModel(x, y, z, tank_cls, fluid_id)
    updateClientTanksOnce()

@ModBlockEntityRemoveClientEvent.Listen()
def onModBlockEntityRemoveClientEvent(event):
    # type: (ModBlockEntityRemoveClientEvent) -> None
    x = event.posX
    y = event.posY
    z = event.posZ
    if (x, y, z) in client_models:
        client_models.pop((x, y, z))[1].Destroy()
    if (x, y, z) in client_tank_datas:
        client_tank_datas.pop((x, y, z))

def loadModel(x, y, z, cls, fluid_id, fluid_volume_pc=None):
    # type: (int, int, int, type[BasicTank], str, float | None) -> FluidModel
    if (x, y, z) in client_models:
        return client_models[(x, y, z)][1]
    else:
        fluid_id_input = fluid_id
        model = FluidModel(x, y, z, fluid_id_input, fluid_volume_pc)
        client_models[(x, y, z)] = (cls, model)
        return model

def getFluidDataFromBlock(block_entity_data):
    # type: (dict) -> tuple[str | None, float]
    ex_data = block_entity_data["exData"]
    if K_FLUID_ID not in ex_data:
        return None, 0
    fluid_id_datas = ex_data[K_FLUID_ID]
    if fluid_id_datas["__type__"] == 1:
        # None
        return None, ex_data[K_FLUID_VOLUME]["__value__"]
    return ex_data[K_FLUID_ID]["__value__"], ex_data[K_FLUID_VOLUME]["__value__"]

def getModelScaleRel(fluid_volume, max_volume):
    # type: (float, float) -> float
    if fluid_volume == INFINITY:
        return 1
    elif max_volume == INFINITY:
        return 0
    elif max_volume == 0:
        return 2
    else:
        return fluid_volume / max_volume

def updateClientTanksOnce():
    for (x, y, z), (tank_cls, old_fluid_id, old_fluid_volume) in client_tank_datas.copy().items():
        blockdata = GetBlockEntityData(x, y, z)
        if blockdata is None:
            print("[ERROR] Tank: BlockEntityData is None")
            continue
        fluid_id, fluid_volume = getFluidDataFromBlock(blockdata)
        if fluid_volume == INFINITY:
            vol_pc = 1
        elif tank_cls.max_fluid_volume == INFINITY:
            vol_pc = 0
        else:
            vol_pc = float(fluid_volume) / tank_cls.max_fluid_volume
        if fluid_id != old_fluid_id:
            if old_fluid_id is None and fluid_id is not None:
                loadModel(x, y, z, tank_cls, fluid_id, vol_pc).SetTexture(fluid_id)
            elif old_fluid_id is not None and fluid_id is None:
                client_models.pop((x, y, z))[1].Destroy()
            elif old_fluid_id is not None and fluid_id is not None:
                client_models.pop((x, y, z))[1].Destroy()
                loadModel(x, y, z, tank_cls, fluid_id, vol_pc)
            client_tank_datas[(x, y, z)] = (tank_cls, fluid_id, fluid_volume)
        if fluid_id is not None and fluid_volume != old_fluid_volume:
            loadModel(x, y, z, tank_cls, fluid_id).SetYScale(vol_pc)
            

@ClientInitCallback()
@AsTimerFunc(0.2)
def updateClientTanks():
    updateClientTanksOnce()

