# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ...common.define import flags
from ...common.events.machinery.hydroponic_bed import (
    HydroponicBedModelUpdateEvent,
    HydroponicBedModelUpdatesEvent,
)
from ...common.define.id_enum.machinery import HYDROPONIC_BED as MACHINE_ID
from ...common.machinery_def.hydroponic_bed import (
    HydroponicBedRecipe,
    recipes as Recipes,
)
from ...common.ui_sync.machinery.hydroponic_bed import HydroponicBedUISync
from ...common.utils.block_sync import BlockSync
from .basic import (
    ItemContainer,
    GUIControl,
    PowerControl,
    WorkRenderer,
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

block_sync = BlockSync(MACHINE_ID, side=BlockSync.SIDE_SERVER)


@RegisterMachine
class HydroponicBed(ItemContainer, GUIControl, PowerControl, WorkRenderer):
    block_name = MACHINE_ID
    input_slots = (0,)
    running_power = POWER_COST

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        self.sync = HydroponicBedUISync.NewServer(self).Activate()
        seed_item = self.GetSlotItem(0)
        self.crop_id = seed_item.id if seed_item else None
        self.ticks = 0
        self.CallSync()

    @SuperExecutorMeta.execute_super
    def OnUnload(self):
        # type: () -> None
        block_sync.discard_block((self.dim, self.x, self.y, self.z))

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
                    self.work_once()
                    self.CallSync()

    def OnSync(self):
        # type: () -> None
        self.sync.store_rf = self.store_rf
        self.sync.rf_max = self.store_rf_max
        self.sync.grow_stage = self.grow_stage
        if self.crop_id is not None:
            self.sync.crop_id = Recipes.recipes_mapping[self.crop_id].crop_block_id
        else:
            self.sync.crop_id = None
        self.sync.MarkedAsChanged()

    def IsValidInput(self, slot, item):
        # type: (int, Item) -> bool
        return item.id in Recipes.recipes_mapping

    @SuperExecutorMeta.execute_super
    def OnSlotUpdate(self, slot_pos):
        # type: (int) -> None
        seed_item = self.GetSlotItem(0)
        self.crop_id = seed_item.id if seed_item else None
        if self.crop_id is None:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
        elif self.crop_id in Recipes:
            self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
        self.CallSync()
        self.notifyUpdate()

    @SuperExecutorMeta.execute_super
    def SetDeactiveFlag(self, flag):
        pass

    def work_once(self):
        if self.crop_id is not None:
            self.stage_grow_ticks += WORK_TICK_DELAY
            if (
                self.stage_grow_ticks
                >= Recipes.recipes_mapping[self.crop_id].grow_stage_ticks
            ):
                self.grow_stage += 1
                self.stage_grow_ticks = 0
                if self.grow_stage + 1 >= Recipes.recipes_mapping[self.crop_id].stages:
                    self.finish_once(Recipes.recipes_mapping[self.crop_id])
                    self.grow_stage = 0
                self.notifyUpdate()

    def takeWater(self):
        if self.water_store < MAX_WATER_STORE / 2:
            from .hydroponic_base import HydroponicBase

            m = GetMachineStrict(self.dim, self.x, self.y - 1, self.z)
            if isinstance(m, HydroponicBase):
                vol = m.GetWaterVolume()
                req_water = min(vol, MAX_WATER_STORE - self.water_store)
                if req_water > 0:
                    self.water_store += req_water
                    m.TakeWater(req_water)
        if self.water_store >= ONCE_WATER_COST:
            self.water_store -= ONCE_WATER_COST
            return True
        else:
            return False

    def finish_once(self, recipe):
        # type: (HydroponicBedRecipe) -> None
        from .hydroponic_base import HydroponicBase

        out_seed_count = recipe.rand_seed_count() - 1
        m = GetMachineStrict(self.dim, self.x, self.y - 1, self.z)
        if isinstance(m, HydroponicBase):
            m.OutputItem(Item(recipe.seed_item, count=out_seed_count))
            for out_crop in recipe.rand_harvest_output():
                m.OutputItem(Item(out_crop.id))

    def notifyUpdate(self):
        if self.crop_id is None:
            crop_block_id = None
        else:
            crop_block_id = Recipes.recipes_mapping[self.crop_id].crop_block_id
        HydroponicBedModelUpdateEvent(
            self.x, self.y, self.z, crop_block_id, self.grow_stage
        ).sendMulti(block_sync.get_players((self.dim, self.x, self.y, self.z)))

    @property
    def grow_stage(self):
        # type: () -> int
        return self.bdata[K_GROW_STAGE] or 0

    @grow_stage.setter
    def grow_stage(self, value):
        # type: (int) -> None
        self.bdata[K_GROW_STAGE] = value

    @property
    def stage_grow_ticks(self):
        # type: () -> int
        return self.bdata[K_STAGE_GROW_TICKS] or 0

    @stage_grow_ticks.setter
    def stage_grow_ticks(self, value):
        # type: (int) -> None
        self.bdata[K_STAGE_GROW_TICKS] = value

    @property
    def water_store(self):
        # type: () -> float
        return self.bdata[K_WATER_STORE] or 0.0

    @water_store.setter
    def water_store(self, value):
        # type: (float) -> None
        self.bdata[K_WATER_STORE] = value
