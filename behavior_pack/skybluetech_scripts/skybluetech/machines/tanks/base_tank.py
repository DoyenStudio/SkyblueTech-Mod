# coding=utf-8
#
from mod.server.blockEntityData import BlockEntityData
from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.general import ClientInitCallback
from skybluetech_scripts.tooldelta.api.timer import AsTimerFunc
from skybluetech_scripts.tooldelta.api.client.entity import CreateDropItemModelEntity, SetDropItemTransform, DeleteClientDropItemEntity
from skybluetech_scripts.tooldelta.api.client.block import GetBlockEntityData
from skybluetech_scripts.tooldelta.events.client import ModBlockEntityLoadedClientEvent, ModBlockEntityRemoveClientEvent
from ...define.fluids.texture import getBaseTexture
from ...ui_sync.machines.general_tank import GeneralTankUISync
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


class FluidModel:
    def __init__(self, xyz, fluid_id):
        # type: (tuple[int, int, int], str) -> None
        
        x, y, z = xyz
        scale = 2.1
        YD_OFFSET = -0.02
        dim = 0 # ClientGetPlayerDimensionId()
        down_offset = (x+0.5, y-0.32, z+0.3)
        down_rotation = (90, 0, 0)
        up_offset = (x+0.5, y+0.6, z+0.3)
        up_rotation = (90, 0, 0)
        north_offset = (x+0.5, y+YD_OFFSET, z+0.06)
        north_rotation = (0, 0, 0)
        south_offset = (x+0.5, y+YD_OFFSET, z+0.98)
        south_rotation = (0, 0, 0)
        west_offset = (x+0.08, y+YD_OFFSET, z+0.5)
        west_rotation = (0, 90, 0)
        east_offset = (x+0.98, y+YD_OFFSET, z+0.5)
        east_rotation = (0, 90, 0)
        self.down_model = CreateDropItemModelEntity(dim, down_offset, Item(fluid_id, count=1))
        self.up_model = CreateDropItemModelEntity(dim, up_offset, Item(fluid_id, count=1))
        self.north_model = CreateDropItemModelEntity(dim, north_offset, Item(fluid_id, count=1))
        self.south_model = CreateDropItemModelEntity(dim, south_offset, Item(fluid_id, count=1))
        self.west_model = CreateDropItemModelEntity(dim, west_offset, Item(fluid_id, count=1))
        self.east_model = CreateDropItemModelEntity(dim, east_offset, Item(fluid_id, count=1))
        SetDropItemTransform(self.down_model, None, down_rotation, scale)
        SetDropItemTransform(self.up_model, None, up_rotation, scale)
        SetDropItemTransform(self.north_model, None, north_rotation, scale)
        SetDropItemTransform(self.south_model, None, south_rotation, scale)
        SetDropItemTransform(self.west_model, None, west_rotation, scale)
        SetDropItemTransform(self.east_model, None, east_rotation, scale)

    def Destroy(self):
        DeleteClientDropItemEntity(self.down_model)
        DeleteClientDropItemEntity(self.up_model)
        DeleteClientDropItemEntity(self.north_model)
        DeleteClientDropItemEntity(self.south_model)
        DeleteClientDropItemEntity(self.east_model)
        DeleteClientDropItemEntity(self.west_model)

def RegisterTank(tank_class):
    # type: (type[BasicTank]) -> type[BasicTank]
    registered_tanks[tank_class.block_name] = tank_class
    return tank_class


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

def loadModel(x, y, z, cls, fluid_id):
    # type: (int, int, int, type[BasicTank], str) -> FluidModel
    if (x, y, z) in client_models:
        return client_models[(x, y, z)][1]
    else:
        fluid_id_input = fluid_id
        model = FluidModel((x, y, z), fluid_id_input)
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
            continue
        fluid_id, fluid_volume = getFluidDataFromBlock(blockdata)
        if fluid_id != old_fluid_id:
            if old_fluid_id is None and fluid_id is not None:
                loadModel(x, y, z, tank_cls, fluid_id)
            elif old_fluid_id is not None and fluid_id is None:
                client_models.pop((x, y, z))[1].Destroy()
            elif old_fluid_id is not None and fluid_id is not None:
                client_models.pop((x, y, z))[1].Destroy()
                loadModel(x, y, z, tank_cls, fluid_id)
            client_tank_datas[(x, y, z)] = (tank_cls, fluid_id, fluid_volume)
            

@ClientInitCallback()
@AsTimerFunc(0.2)
def updateClientTanks():
    updateClientTanksOnce()

