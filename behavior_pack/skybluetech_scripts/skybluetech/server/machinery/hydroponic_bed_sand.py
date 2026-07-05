# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ...common.define import flags
from ...common.define.id_enum.machinery import Machinery
MACHINE_ID = Machinery.HYDROPONIC_BED_SAND
from ...common.machinery_def.hydroponic_bed_sand import (
    HydroponicBedSandRecipe,
    recipes as Recipes,
    K_CROP_BLOCK_ID,
    K_GROW_PROGRESS,
    K_WATER_STORE,
    STORE_RF_MAX,
    POWER_COST,
    WORK_TICK_DELAY,
    MAX_WATER_STORE,
    ONCE_WATER_COST,
)
from .basic import (
    ItemContainer,
    GUIControl,
    BaseSpeedControl,
    PowerControl,
    WorkRenderer,
    RegisterMachine,
)
from .pool import GetMachineStrict


@RegisterMachine
class HydroponicBedSand(
    BaseSpeedControl, ItemContainer, GUIControl, PowerControl, WorkRenderer
):
    block_name = MACHINE_ID
    store_rf_max = STORE_RF_MAX
    input_slots = (0,)
    running_power = POWER_COST
    original_speed = WORK_TICK_DELAY

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        seed_item = self.GetSlotItem(0)
        self.crop_id = (
            seed_item.id
            if seed_item and seed_item.id in Recipes.recipes_mapping
            else None
        )
        self.set_crop_block_id(
            Recipes.recipes_mapping[self.crop_id].crop_block_id
            if self.crop_id is not None
            else None
        )

    @SuperExecutorMeta.execute_super
    def OnUnload(self):
        # type: () -> None
        pass

    def OnTicking(self):
        # type: () -> None
        if self.IsActive():
            if BaseSpeedControl.ProcessOnce(self):
                if self.PowerEnough():
                    if not self.take_water():
                        return
                    self.ReducePower()
                    self.work_once()

    def IsValidInput(self, slot, item):
        # type: (int, Item) -> bool
        return item.id in Recipes.recipes_mapping

    @SuperExecutorMeta.execute_super
    def OnSlotUpdate(self, slot_pos):
        # type: (int) -> None
        seed_item = self.GetSlotItem(0)
        self.crop_id = (
            seed_item.id
            if seed_item and seed_item.id in Recipes.recipes_mapping
            else None
        )
        self.set_crop_block_id(
            Recipes.recipes_mapping[self.crop_id].crop_block_id
            if self.crop_id is not None
            else None
        )
        self.grow_progress = 0.0
        if self.crop_id is None:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
        else:
            self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)

    @SuperExecutorMeta.execute_super
    def SetDeactiveFlag(self, flag):
        pass

    def work_once(self):
        if self.crop_id is not None:
            self.grow_progress += Recipes.recipes_mapping[
                self.crop_id
            ].once_grow_progress
            if self.grow_progress >= 1.0:
                self.finish_once(Recipes.recipes_mapping[self.crop_id])
                self.grow_progress = 0.0

    def take_water(self):
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
        # type: (HydroponicBedSandRecipe) -> None
        from .hydroponic_base import HydroponicBase

        m = GetMachineStrict(self.dim, self.x, self.y - 1, self.z)
        if isinstance(m, HydroponicBase):
            for out_crop in recipe.harvest_outputs:
                m.OutputItem(Item(out_crop.id, count=int(out_crop.count)))

    def set_crop_block_id(self, value):
        # type: (str | None) -> None
        self.bdata[K_CROP_BLOCK_ID] = value

    @property
    def grow_progress(self):
        # type: () -> float
        return self.bdata[K_GROW_PROGRESS] or 0.0

    @grow_progress.setter
    def grow_progress(self, value):
        # type: (float) -> None
        self.bdata[K_GROW_PROGRESS] = value

    @property
    def water_store(self):
        # type: () -> float
        return self.bdata[K_WATER_STORE] or 0.0

    @water_store.setter
    def water_store(self, value):
        # type: (float) -> None
        self.bdata[K_WATER_STORE] = value
