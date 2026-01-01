# coding=utf-8
from weakref import WeakValueDictionary as WVDict, WeakKeyDictionary as WKDict
from mod.server.blockEntityData import BlockEntityData
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.events.client import (
    ModBlockEntityLoadedClientEvent,
    ModBlockEntityRemoveClientEvent,
)
from skybluetech_scripts.tooldelta.extensions.singleblock_model_loader import (
    GeometryModel,
    CreateBlankSingleBlockModelEntity,
)
from ..define import flags
from ..define.events.hydroponic_bed import (
    HydroponicBedClientLoadEvent,
    HydroponicBedModelUpdateEvent,
    HydroponicBedModelUpdatesEvent,
    MODE_UNLOAD, MODE_LOAD
)
from ..define.id_enum.machinery import HYDROPONIC_BED as MACHINE_ID
from ..machinery_def.hydroponic_bed import HydroponicBedRecipe, recipes as Recipes
from ..ui_sync.machines.hydroponic_bed import HydroponicBedUISync
from .basic import (
    AutoSaver,
    BaseMachine,
    ItemContainer,
    GUIControl,
    PowerControl,
    RegisterMachine,
)
from .pool import GetMachineStrict

K_GROW_STAGE = "grow_stage"
K_STAGE_GROW_TICKS = "stage_grow_ticks"
K_WATER_STORE = "water_store"
WORK_TICK_DELAY = 5
POWER_COST = 4
ONCE_WATER_COST = 5
MAX_WATER_STORE = 1000


@RegisterMachine
class HydroponicBed(AutoSaver, ItemContainer, GUIControl, PowerControl):
    block_name = MACHINE_ID
    input_slots = (0,)
    running_power = POWER_COST

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        AutoSaver.__init__(self, dim, x, y, z, block_entity_data)
        BaseMachine.__init__(self, dim, x, y, z, block_entity_data)
        ItemContainer.__init__(self, dim, x, y, z, block_entity_data)
        self.sync = HydroponicBedUISync.NewServer(self).Activate()
        seed_item = self.GetSlotItem(0)
        self.crop_id = seed_item.id if seed_item else None
        self.ticks = 0

    def OnLoad(self):
        BaseMachine.OnLoad(self)
        self.grow_stage = self.bdata[K_GROW_STAGE] or 0
        self.stage_grow_ticks = self.bdata[K_STAGE_GROW_TICKS] or 0
        self.water_store = self.bdata[K_WATER_STORE] or 0.0

    def Dump(self):
        # type: () -> None
        BaseMachine.Dump(self)
        self.bdata[K_GROW_STAGE] = self.grow_stage
        self.bdata[K_STAGE_GROW_TICKS] = self.stage_grow_ticks
        self.bdata[K_WATER_STORE] = self.water_store

    def OnUnload(self):
        # type: () -> None
        AutoSaver.OnUnload(self)
        BaseMachine.OnUnload(self)
        GUIControl.OnUnload(self)

    def OnTicking(self):
        # type: () -> None
        if self.IsActive():
            self.ticks += 1
            if self.ticks >= WORK_TICK_DELAY:
                self.ticks = 0
                if self.PowerEnough():
                    if not self.takeWater():
                        return
                    self.ReducePower()
                    self.workOnce()
                    self.OnSync()

    def OnSync(self):
        # type: () -> None
        self.sync.store_rf = self.store_rf
        self.sync.rf_max = self.store_rf_max
        self.sync.grow_stage = self.grow_stage
        if self.crop_id is not None:
            self.sync.crop_id = Recipes[self.crop_id].crop_block_id
        else:
            self.sync.crop_id = None
        self.sync.MarkedAsChanged()

    def IsValidInput(self, slot, item):
        # type: (int, Item) -> bool
        return item.id in Recipes

    def workOnce(self):
        if self.crop_id is not None:
            self.stage_grow_ticks += WORK_TICK_DELAY
            if self.stage_grow_ticks >= Recipes[self.crop_id].grow_stage_ticks:
                self.grow_stage += 1
                self.stage_grow_ticks = 0
                if self.grow_stage + 1 >= Recipes[self.crop_id].stages:
                    self.finishOnce(Recipes[self.crop_id])
                    self.grow_stage = 0
                self.notifyUpdate()

    def takeWater(self):
        if self.water_store < MAX_WATER_STORE / 2:
            from .hydroponic_base import HydroponicBase
            m = GetMachineStrict(self.dim, self.x, self.y - 1, self.z)
            if isinstance(m, HydroponicBase):
                vol = m.GetWaterVolume()
                if vol < MAX_WATER_STORE / 2:
                    m.RequireFluidsFromNetwork()
                req_water = min(vol, MAX_WATER_STORE - self.water_store)
                if req_water > 0:
                    self.water_store += req_water
                    m.TakeWater(req_water)
                m.RequireAnyFluidFromNetwork()
        if self.water_store >= ONCE_WATER_COST:
            self.water_store -= ONCE_WATER_COST
            return True
        else:
            return False

    def finishOnce(self, recipe):
        # type: (HydroponicBedRecipe) -> None
        from .hydroponic_base import HydroponicBase
        out_seed_count = recipe.rand_seed_count() - 1
        m = GetMachineStrict(self.dim, self.x, self.y - 1, self.z)
        if isinstance(m, HydroponicBase):
            m.OutputItem(Item(recipe.seed_item, count=out_seed_count))
            for out_crop in recipe.rand_harvest_output():
                m.OutputItem(Item(out_crop.id))

    def OnSlotUpdate(self, slot_pos):
        # type: (int) -> None
        seed_item = self.GetSlotItem(0)
        self.crop_id = seed_item.id if seed_item else None
        if self.crop_id is None:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
        elif self.crop_id in Recipes:
            self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
        self.OnSync()
        self.notifyUpdate()

    def notifyUpdate(self):
        if self.crop_id is None:
            crop_block_id = None
        else:
            crop_block_id = Recipes[self.crop_id].crop_block_id
        pids = S_machinery2clis.get(self)
        if pids:
            HydroponicBedModelUpdateEvent(
                self.x, self.y, self.z, crop_block_id, self.grow_stage
            ).sendMulti(list(pids))


S_cli_loaded_machinerys = WVDict()  # type: WVDict[tuple[int, int, int, int], HydroponicBed]
S_machinery2clis = WKDict() # type: WKDict[HydroponicBed, set[str]]

@HydroponicBedClientLoadEvent.Listen()
def onC2SModBlockLoadEvent(event):
    # type: (HydroponicBedClientLoadEvent) -> None
    key = (event.dim, event.x, event.y, event.z)
    if event.mode == MODE_LOAD:
        if key not in S_cli_loaded_machinerys:
            m = GetMachineStrict(event.dim, event.x, event.y, event.z)
            if not isinstance(m, HydroponicBed):
                return
        S_cli_loaded_machinerys[key] = m
        S_machinery2clis.setdefault(m, set()).add(event.player_id)
        m.notifyUpdate()
    elif event.mode == MODE_UNLOAD:
        if key not in S_cli_loaded_machinerys:
            return
        m = S_cli_loaded_machinerys[key]
        S_machinery2clis.get(m, set()).discard(event.player_id)

C_loaded_models = {}  # type: dict[tuple[int, int, int], GeometryModel]

@ModBlockEntityLoadedClientEvent.Listen()
def onModBlockLoaded(event):
    # type: (ModBlockEntityLoadedClientEvent) -> None
    if event.blockName == HydroponicBed.block_name:
        C_loaded_models[
            (event.posX, event.posY, event.posZ)
        ] = CreateBlankSingleBlockModelEntity((event.posX, event.posY+3.0/16, event.posZ))
        HydroponicBedClientLoadEvent(
            event.dimensionId, event.posX, event.posY, event.posZ, MODE_LOAD
        ).send()

@ModBlockEntityRemoveClientEvent.Listen()
def onModBlockRemoved(event):
    # type: (ModBlockEntityRemoveClientEvent) -> None
    if event.blockName == HydroponicBed.block_name:
        HydroponicBedClientLoadEvent(
            event.dimensionId, event.posX, event.posY, event.posZ, MODE_UNLOAD
        ).send()
        model = C_loaded_models.pop((event.posX, event.posY, event.posZ), None)
        if model is not None:
            model.Destroy()

@HydroponicBedModelUpdateEvent.Listen()
def onS2CUpdate(event):
    # type: (HydroponicBedModelUpdateEvent) -> None
    key = (event.x, event.y, event.z)
    if event.crop_id is None:
        model = C_loaded_models.get(key, None)
        if model is not None:
            model.SetBlockModel("minecraft:air", 0)
    elif event.crop_id is not None:
        model = C_loaded_models.get(key)
        if model is not None:
            model.SetBlockModel(event.crop_id, event.aux)
