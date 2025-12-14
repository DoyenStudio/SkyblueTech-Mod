# coding=utf-8
#
from mod.server.blockEntityData import BlockEntityData
from skybluetech_scripts.tooldelta.define.item import Item
from ..define import flags
from ..define.events.fermenter import FermenterSetTemperatureEvent
from ..define.machine_config.fermenter import *
from ..ui_sync.machines.fermenter import FermenterUISync
from ..utils.action_commit import SafeGetMachine
from .basic import (
    BaseMachine,
    GUIControl,
    MultiBlockStructure,
    UpgradeControl,
    WorkRenderer,
    RegisterMachine,
)
from .basic.multi_block_structure import (
    GenerateSimpleStructureTemplate,
)
from .interfaces import (
    EnergyInputInterface,
    FluidInputInterface,
    FluidOutputInterface,
    ItemInputInterface,
)


pal = GenerateSimpleStructureTemplate(
    STRUCTURE_PATTERN_MAPPING,
    STRUCTURE_PATTERN,
    require_blocks_count=STRUCTURE_REQUIRE_BLOCKS,
)

K_TEMPERATURE = "st:temp"
K_EXPECTED_TEMPERTURE = "st:expected_temp"
K_VOLUME = "st:volume"
K_THICKNESS = "st:thickness"
K_MUD_VATILATY = "st:mud_vitalaty"
K_RECIPE = "st:recipe"
K_CELL_HUNGER = "st:bacteria_hunger"
K_INOCULATING_RECIPE = "st:inoculate_recipe"
K_INOCULATE_TIME = "st:inoculate_time"


@RegisterMachine
class Fermenter(GUIControl, MultiBlockStructure, UpgradeControl, WorkRenderer):
    block_name = "skybluetech:fermenter_controller"
    origin_process_ticks = 1
    running_power = 5
    structure_palette = pal
    input_slots = (0, 1)
    fluid_io_mode = (2, 2, 2, 2, 2, 2)
    fluid_input_slots = {0}
    fluid_output_slots = {1, 2}
    fluid_slot_max_volumes = (1000, 1000, 1000)
    work_ticks_delay = 5
    functional_block_ids = {
        IO_ENERGY,
        IO_ITEM,
        IO_FLUID1,
        IO_FLUID2,
        IO_GAS,
    }

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        MultiBlockStructure.__init__(self, dim, x, y, z, block_entity_data)
        self.t = 0
        self.sync = FermenterUISync.NewServer(self).Activate()
        UpgradeControl.__init__(self, dim, x, y, z, block_entity_data)
        self.OnSync()

    def OnTicking(self):
        self.t += 1
        if self.t >= self.work_ticks_delay:
            self.t = 0
            if self.IsActive():
                if self.ProcessOnce():
                    self.workOnce()
                    self.OnSync()
            if self.IsActiveIgnoreCondition(flags.DEACTIVE_FLAG_POWER_LACK):
                self.tryInoculate()
                recipe = spec_recipes.get(self.recipe_id)
                if recipe is None:
                    return
                self.lifeCycle(recipe)

    def OnLoad(self):
        UpgradeControl.OnLoad(self)
        self.mud_temperature = self.bdata[K_TEMPERATURE] or 25.0
        self.mud_thickness = self.bdata[K_THICKNESS] or 0.0
        self.mud_vitality = self.bdata[K_MUD_VATILATY] or 0.0
        self.content_volume = self.bdata[K_VOLUME] or 0.0
        self.bacteria_hunger = self.bdata[K_CELL_HUNGER] or 0.0
        self.expected_mud_temperature = self.bdata[K_EXPECTED_TEMPERTURE] or 25.0
        self.recipe_id = self.bdata[K_RECIPE] or 0
        self.current_inoculating_recipe = self.bdata[K_INOCULATING_RECIPE] or 0
        self.current_inoculate_time = self.bdata[K_INOCULATE_TIME] or 0.0
        MultiBlockStructure.OnLoad(self)

    def OnStructureChanged(self, ok):
        # type: (bool) -> None
        if ok:
            self.getEnergyInIO().SetMachineRef(self)
            self.getItemInIO().OnSlotUpdate = self.OnOtherSlotUpdate

    def Dump(self):
        # type: () -> None
        UpgradeControl.Dump(self)
        self.bdata[K_TEMPERATURE] = self.mud_temperature
        self.bdata[K_THICKNESS] = self.mud_thickness
        self.bdata[K_MUD_VATILATY] = self.mud_vitality
        self.bdata[K_VOLUME] = self.content_volume
        self.bdata[K_CELL_HUNGER] = self.bacteria_hunger
        self.bdata[K_EXPECTED_TEMPERTURE] = self.expected_mud_temperature
        self.bdata[K_RECIPE] = self.recipe_id
        self.bdata[K_INOCULATING_RECIPE] = self.current_inoculating_recipe
        self.bdata[K_INOCULATE_TIME] = self.current_inoculate_time

    def OnUnload(self):
        # type: () -> None
        BaseMachine.OnUnload(self)
        GUIControl.OnUnload(self)
        MultiBlockStructure.OnUnload(self)

    def OnSync(self):
        self.sync.store_rf = self.store_rf
        self.sync.store_rf_max = self.store_rf_max
        self.sync.mud_temperature = self.mud_temperature
        self.sync.mud_thickness = self.mud_thickness
        self.sync.content_volume_pc = float(self.content_volume) / POOL_MAX_VOLUME
        self.sync.expected_temperature = self.expected_mud_temperature
        self.sync.recipe_id = self.recipe_id
        self.sync.structure_status = self._last_destroy_flag
        self.sync.structure_lack_blocks = self._lacked_blocks
        if self.sync.structure_status == 0:
            self.sync.out_gas_id = self.getGasOutIO().fluid_id
            self.sync.out_gas_volume = self.getGasOutIO().fluid_volume
            self.sync.out_gas_max_volume = self.getGasOutIO().max_fluid_volume
            self.sync.out_fluid_id = self.getFluidOutIO().fluid_id
            self.sync.out_fluid_volume = self.getFluidOutIO().fluid_volume
            self.sync.out_fluid_max_volume = self.getFluidOutIO().max_fluid_volume
        else:
            self.sync.out_gas_id = None
            self.sync.out_gas_volume = 0.0
            self.sync.out_gas_max_volume = 1.0
            self.sync.out_fluid_id = None
            self.sync.out_fluid_volume = 0.0
            self.sync.out_fluid_max_volume = 1.0
        self.sync.MarkedAsChanged()


    def OnSlotUpdate(self, slot_pos):
        # type: (int) -> None
        if slot_pos == 0:
            # 接种槽
            slotitem = self.GetSlotItem(0)
            if slotitem is None:
                if self.current_inoculating_recipe != 0:
                    self.current_inoculate_time = 0
                    self.current_inoculating_recipe = 0
                return
            if self.current_inoculating_recipe != 0:
                recipe = spec_recipes[self.current_inoculating_recipe]
                if slotitem.id != recipe.vitality_matter:
                    self.current_inoculate_time = 0
                    self.current_inoculating_recipe = 0
            elif self.current_inoculate_time == 0:
                if self.mud_thickness > 0 and self.mud_thickness < 0.1:
                    # 菌种浓度太低
                    recipe = spec_recipes[self.recipe_id]
                    if slotitem.id != recipe.vitality_matter:
                        self.current_inoculate_time = 0.0
                        self.current_inoculating_recipe = 0
                    else:
                        self.current_inoculating_recipe = self.recipe_id
                else:
                    # 初始化一个菌种
                    for recipe_id, recipe in spec_recipes.items():
                        if recipe.vitality_matter == slotitem.id:
                            self.current_inoculate_time = 0.0
                            self.current_inoculating_recipe = recipe_id
                            print("Set to", recipe_id)
                            break

    def OnOtherSlotUpdate(self, slot_pos):
        # type: (int) -> None
        pass

    def IsValidInput(self, slot, item):
        # type: (int, Item) -> bool
        if self.InUpgradeSlot(slot):
            return UpgradeControl.IsValidInput(self, slot, item)
        elif slot == 0:
            for recipe in spec_recipes.values():
                if item.id == recipe.vitality_matter:
                    return True
            return False
        elif slot == 1:
            if self.recipe_id == 0:
                return False
            recipe = spec_recipes[self.recipe_id]
            if item.id != recipe.nutrition_matter:
                return False
            return True
        else:
            return False

    def SetDeactiveFlag(self, flag):
        # type: (int) -> None
        BaseMachine.SetDeactiveFlag(self, flag)
        UpgradeControl.SetDeactiveFlag(self, flag)
        WorkRenderer.SetDeactiveFlag(self, flag)

    def setExpectedTemperature(self, temperature):
        # type: (float) -> None
        if temperature < TEMPERATURE_MIN or temperature > TEMPERATURE_MAX:
            return
        self.expected_mud_temperature = temperature
        if self.expected_mud_temperature < 25:
            self.SetPower(3 + int(25 - self.expected_mud_temperature))
        elif self.expected_mud_temperature > 30:
            self.SetPower(3 + int(self.expected_mud_temperature - 30))
        else:
            self.SetPower(3)
        self.OnSync()

    def workOnce(self):
        self.tryAddWater()
        self.tryCtrlTemperature()

    def lifeCycle(self, recipe):
        # type: (FermenterRecipe) -> None
        self.bacteria_hunger -= HUNGER_REDUCE
        self.tryEat(recipe)
        self.updateVitality(recipe)
        self.tryGrow(recipe)
        self.tryProduce(recipe)

    def tryCtrlTemperature(self):
        if self.mud_temperature < self.expected_mud_temperature:
            self.mud_temperature += min(
                (self.expected_mud_temperature - self.mud_temperature) * 0.002,
                0.01
            )
        elif self.mud_temperature > self.expected_mud_temperature:
            self.mud_temperature -= min(
                (self.mud_temperature - self.expected_mud_temperature) * 0.002,
                0.01
            )

    def tryAddWater(self):
        if self.content_volume < POOL_MAX_VOLUME and self.getWaterInIO().fluid_volume > 50:
            prev_vol = self.content_volume
            self.content_volume += 50
            self.getWaterInIO().fluid_volume -= 50
            self.mud_thickness *= float(prev_vol) / self.content_volume

    def tryEat(self, recipe):
        # type: (FermenterRecipe) -> None
        if self.bacteria_hunger <= 0:
            maybe_food = self.GetSlotItem(1)
            if maybe_food is None or maybe_food.id != recipe.nutrition_matter:
                return
            maybe_food.count -= 1
            self.SetSlotItem(1, maybe_food)
            self.bacteria_hunger += recipe.nutrition_count
            self.mud_vitality += recipe.vitality_count
            11111

    def tryInoculate(self):
        # type: () -> None
        if self.current_inoculating_recipe != 0:
            print("growing", self.current_inoculate_time)
            recipe = spec_recipes[self.current_inoculating_recipe]
            self.current_inoculate_time += float(self.work_ticks_delay) / 20
            if self.current_inoculate_time >= recipe.inoculate_time:
                self.mud_thickness += recipe.vitality_count
                self.recipe_id = self.current_inoculating_recipe
                self.current_inoculating_recipe = 0
                self.current_inoculate_time = 0.0
                slotitem = self.GetSlotItem(1)
                if slotitem is not None:
                    slotitem.count -= 1
                    self.SetSlotItem(1, slotitem)

    def tryGrow(self, recipe):
        # type: (FermenterRecipe) -> None
        grow_speed = self.getGrowSpeed(recipe)
        mud_vol = self.content_volume * self.mud_thickness
        mud_vol_add = POOL_MAX_VOLUME * grow_speed
        water_vol = self.content_volume - mud_vol
        self.mud_thickness = float(max(0, mud_vol + mud_vol_add)) / (
            mud_vol + mud_vol_add + water_vol
        )

    def tryProduce(self, recipe):
        # type: (FermenterRecipe) -> None
        if self.mud_thickness < recipe.produce_thickness:
            return
        self.content_volume -= recipe.volume_reduce
        if self.getGasOutIO().fluid_id == recipe.out_gas_id:
            self.getGasOutIO().fluid_volume += recipe.out_gas_volume
        if self.getGasOutIO().fluid_id == recipe.out_fluid_id:
            self.getGasOutIO().fluid_volume += recipe.out_fluid_volume

    def updateVitality(self, recipe):
        # type: (FermenterRecipe) -> None
        mud_temp = self.mud_temperature
        min_temp = recipe.min_temperature
        max_temp = recipe.max_temperature
        fit_temp = recipe.fit_temperature
        if mud_temp > recipe.max_temperature:
            self.mud_vitality = max(
                -1,
                self.mud_vitality
                - float(mud_temp - max_temp) * HI_TEMPERATURE_VITALITY_REDUCE,
            )
        elif mud_temp < min_temp:
            self.mud_vitality = max(
                0,
                self.mud_vitality
                - float(max_temp - mud_temp) * LO_TEMPERATURE_VITALITY_REDUCE,
            )
        elif mud_temp < fit_temp and self.bacteria_hunger > 0:
            self.mud_vitality = min(
                1,
                self.mud_vitality
                + float(mud_temp - mud_temp)
                / (fit_temp - min_temp)
                * VITALITY_ADD_MAX
                * (self.bacteria_hunger / BATERIA_MAX_HUNGER),
            )
        if self.bacteria_hunger < 0:
            self.mud_vitality = max(
                -1,
                self.mud_vitality
                - (self.bacteria_hunger / BATERIA_MIN_HUNGER)
                * VITALITY_HUNGER_REDUCE_MAX,
            )

    def updateTemperature(self):
        if self.mud_temperature < 25:
            self.mud_temperature += 0.02
        elif self.mud_temperature > 30:
            self.mud_temperature -= 0.02

    def getGrowSpeed(self, recipe):
        # type: (FermenterRecipe) -> float
        return self.mud_vitality * recipe.max_grow_speed

    def getItemInIO(self):
        return self.GetMachine(ItemInputInterface, IO_ITEM)

    def getEnergyInIO(self):
        return self.GetMachine(EnergyInputInterface, IO_ENERGY)

    def getWaterInIO(self):
        return self.GetMachine(FluidInputInterface, IO_FLUID1)

    def getFluidOutIO(self):
        return self.GetMachine(FluidOutputInterface, IO_FLUID2)

    def getGasOutIO(self):
        return self.GetMachine(FluidOutputInterface, IO_GAS)


@FermenterSetTemperatureEvent.Listen()
def onFermenterSetTemperatureEvent(event):
    # type: (FermenterSetTemperatureEvent) -> None
    global Fermenter
    m = SafeGetMachine(event.x, event.y, event.z, event.player_id)
    if not isinstance(m, Fermenter):
        return
    if not isinstance(event.temperature, float):
        return
    m.setExpectedTemperature(event.temperature)
