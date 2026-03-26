# coding=utf-8
from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ...common.define import flags
from ...common.events.machinery.fermenter import (
    FermenterSetTemperatureEvent,
    FermenterSeMaxVolumeEvent,
)
from ...common.define.id_enum.machinery import FERMENTER as MACHINE_ID
from ...common.machinery_def.fermenter import *
from ...common.ui_sync.machinery.fermenter import FermenterUISync
from .utils.action_commit import SafeGetMachine
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
K_EXPECTED_WATER_MAX_VOLUME = "st:expected_max_volume"
K_MUD_VOLUME = "st:mud_volume"
K_WATER_VOLUME = "st:water_volume"
K_MUD_VITALITY = "st:mud_vitality"
K_RECIPE = "st:recipe"
K_CELL_HUNGER = "st:bacteria_hunger"
K_INOCULATING_RECIPE = "st:inoculate_recipe"
K_INOCULATE_TIME = "st:inoculate_time"

EnergyInputInterface.AddExtraMachineId(IO_ENERGY)
FluidInputInterface.AddExtraMachineId(IO_FLUID1)
FluidOutputInterface.AddExtraMachineId(IO_FLUID2)
FluidOutputInterface.AddExtraMachineId(IO_GAS)
ItemInputInterface.AddExtraMachineId(IO_ITEM)


@RegisterMachine
class Fermenter(GUIControl, MultiBlockStructure, UpgradeControl, WorkRenderer):
    block_name = MACHINE_ID
    origin_process_ticks = 1
    running_power = 5
    structure_palette = pal
    input_slots = (0, 1)
    fluid_io_mode = (2, 2, 2, 2, 2, 2)
    fluid_input_slots = {0}
    fluid_output_slots = {1, 2}
    fluid_slot_max_volumes = (1000, 1000, 1000)
    work_ticks_delay = 5
    upgrade_slot_start = 2
    allow_upgrader_tags = set()
    functional_block_ids = {
        IO_ENERGY,
        IO_ITEM,
        IO_FLUID1,
        IO_FLUID2,
        IO_GAS,
    }

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        self.t = 0
        self.sync = FermenterUISync.NewServer(self).Activate()

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
                self.OnSync()

    def OnStructureChanged(self, ok):
        # type: (bool) -> None
        if ok:
            self.getEnergyInIO().SetMachineRef(self)
            self.getItemInIO().SetOnSlotUpdateCallback(self.OnOtherSlotUpdate)
            # self.getFluidOutIO().SelfRequireFluid()
        self.OnSync()

    @SuperExecutorMeta.execute_super
    def OnUnload(self):
        pass

    def OnSync(self):
        self.sync.store_rf = self.store_rf
        self.sync.store_rf_max = self.store_rf_max
        self.sync.mud_temperature = self.mud_temperature
        self.sync.mud_thickness = self.getThickness()
        self.sync.expected_temperature = self.expected_mud_temperature
        self.sync.expected_water_max_volume = self.expected_water_max_volume
        self.sync.recipe_id = self.recipe_id
        self.sync.structure_status = self.GetStructureDestroyFlag()
        self.sync.structure_lack_blocks = self.GetStructureLackedBlocks()
        if self.sync.structure_status == 0:
            self.sync.content_volume_pc = float(self.getVolume()) / POOL_MAX_VOLUME
            self.sync.out_gas_id = self.getGasOutIO().fluid_id
            self.sync.out_gas_volume = self.getGasOutIO().fluid_volume
            self.sync.out_gas_max_volume = self.getGasOutIO().max_fluid_volume
            self.sync.out_fluid_id = self.getFluidOutIO().fluid_id
            self.sync.out_fluid_volume = self.getFluidOutIO().fluid_volume
            self.sync.out_fluid_max_volume = self.getFluidOutIO().max_fluid_volume
            if self.recipe_id > 0:
                recipe = spec_recipes[self.recipe_id]
                self.sync.gas_product_speed = self.getGasProduceRate(recipe) * (
                    20.0 / self.work_ticks_delay
                )
                self.sync.fluid_product_speed = self.getFluidProduceRate(recipe) * (
                    20.0 / self.work_ticks_delay
                )
        else:
            self.sync.content_volume_pc = 0.0
            self.sync.out_gas_id = None
            self.sync.out_gas_volume = 0.0
            self.sync.out_gas_max_volume = 1.0
            self.sync.out_fluid_id = None
            self.sync.out_fluid_volume = 0.0
            self.sync.out_fluid_max_volume = 1.0
        self.sync.MarkedAsChanged()

    @SuperExecutorMeta.execute_super
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
                if self.mud_volume > 0:
                    recipe = spec_recipes[self.recipe_id]
                    if recipe.inoculate_mud_volume > self.mud_volume:
                        # 菌种浓度太低
                        if slotitem.id != recipe.vitality_matter:
                            self.current_inoculate_time = 0.0
                            self.current_inoculating_recipe = 0
                        else:
                            self.current_inoculating_recipe = self.recipe_id
                elif self.mud_volume == 0:
                    # 初始化一个菌种
                    for recipe_id, recipe in spec_recipes.items():
                        if recipe.vitality_matter == slotitem.id:
                            self.current_inoculate_time = 0.0
                            self.current_inoculating_recipe = recipe_id
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
                if self.current_inoculating_recipe != 0:
                    inoculating_recipe = spec_recipes[self.current_inoculating_recipe]
                    return inoculating_recipe.nutrition_matter == item.id
                return False
            recipe = spec_recipes[self.recipe_id]
            return item.id == recipe.nutrition_matter
        else:
            return False

    @SuperExecutorMeta.execute_super
    def SetDeactiveFlag(self, flag):
        pass

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

    def setExpectedWaterMaxVolume(self, volume):
        # type: (float) -> None
        if volume < 0 or volume > POOL_MAX_VOLUME:
            return
        self.expected_water_max_volume = volume
        self.OnSync()

    def workOnce(self):
        self.tryAddWater()
        self.tryCtrlTemperature()

    def lifeCycle(self, recipe):
        # type: (FermenterRecipe) -> None
        self.bacteria_hunger = max(
            -self.getMaxHunger(recipe),
            self.bacteria_hunger - recipe.hunger_reduce_speed * self.mud_volume,
        )
        self.tryEat(recipe)
        self.updateVitality(recipe)
        interrupted = self.tryGrow(recipe)
        if interrupted:
            return
        self.tryProduce(recipe)

    def tryCtrlTemperature(self):
        if self.mud_temperature < self.expected_mud_temperature:
            self.mud_temperature += min(
                (self.expected_mud_temperature - self.mud_temperature) * 0.1, 1
            )
        elif self.mud_temperature > self.expected_mud_temperature:
            self.mud_temperature -= min(
                (self.mud_temperature - self.expected_mud_temperature) * 0.1, 1
            )

    def tryAddWater(self):
        if (
            self.getVolume() + 50 < self.expected_water_max_volume
            and self.getWaterInIO().fluid_volume > 50
        ):
            self.getWaterInIO().fluid_volume -= 200
            # self.getWaterInIO().SelfRequireFluid()
            self.water_volume += 200

    def tryEat(self, recipe):
        # type: (FermenterRecipe) -> None
        if self.bacteria_hunger < self.getMaxHunger(recipe):
            maybe_food = self.GetSlotItem(1)
            if maybe_food is None or maybe_food.id != recipe.nutrition_matter:
                return
            while self.bacteria_hunger < self.getMaxHunger(recipe):
                if maybe_food.count <= 0:
                    return
                maybe_food.count -= 1
                self.SetSlotItem(1, maybe_food)
                self.bacteria_hunger = min(
                    self.getMaxHunger(recipe),
                    self.bacteria_hunger + float(recipe.nutrition_value),
                )
                self.mud_vitality = min(
                    1, self.mud_vitality + recipe.nutrition_recover_vitality
                )
            self.SetSlotItem(1, maybe_food)

    def tryInoculate(self):
        # type: () -> None
        if self.current_inoculating_recipe != 0:
            recipe = spec_recipes[self.current_inoculating_recipe]
            self.current_inoculate_time += float(self.work_ticks_delay) / 20
            if self.current_inoculate_time >= recipe.inoculate_time:
                slotitem = self.GetSlotItem(0)
                if slotitem is not None:
                    slotitem.count -= 1
                    self.SetSlotItem(0, slotitem)
                    self.mud_volume += recipe.inoculate_mud_volume
                    self.recipe_id = self.current_inoculating_recipe
                    self.bacteria_hunger = recipe.nutrition_value
                self.current_inoculating_recipe = 0
                self.current_inoculate_time = 0.0

    def tryGrow(self, recipe):
        # type: (FermenterRecipe) -> bool
        grow_speed = self.getGrowSpeed(recipe)
        if self.getVolume() + grow_speed <= POOL_MAX_VOLUME:
            if grow_speed > 0:
                self.mud_volume += grow_speed
            elif grow_speed < 0:
                self.mud_volume = max(0, self.mud_volume + grow_speed)
                if self.mud_volume <= 0:
                    self.recipe_id = 0
                    self.bacteria_hunger = 0
                    self.mud_vitality = 0
                    return True
        return False

    def tryProduce(self, recipe):
        # type: (FermenterRecipe) -> None
        if self.getThickness() < recipe.produce_thickness:
            return
        if self.getVolume() <= 0:
            return
        self.mud_volume = max(
            0, self.mud_volume - recipe.volume_reduce_rate * self.mud_volume
        )
        self.water_volume = max(
            0, self.water_volume - recipe.volume_reduce_rate * self.water_volume
        )
        gas_io = self.getGasOutIO()
        fluid_io = self.getFluidOutIO()
        if gas_io.fluid_id is None:
            gas_io.fluid_id = recipe.out_gas_id
        if fluid_io.fluid_id is None:
            fluid_io.fluid_id = recipe.out_fluid_id
        if gas_io.fluid_id == recipe.out_gas_id:
            gas_io.AddFluid(recipe.out_gas_id, self.getGasProduceRate(recipe))
        if fluid_io.fluid_id == recipe.out_fluid_id:
            fluid_io.AddFluid(recipe.out_fluid_id, self.getFluidProduceRate(recipe))

    def updateVitality(self, recipe):
        # type: (FermenterRecipe) -> None
        mud_temp = self.mud_temperature
        min_temp = recipe.min_temperature
        max_temp = recipe.max_temperature
        fit_temp = recipe.fit_temperature
        if mud_temp > max_temp:
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
                + VITALITY_ADD_MAX * (self.bacteria_hunger / self.getMaxHunger(recipe)),
            )
        if self.bacteria_hunger < 0:
            self.mud_vitality = max(
                -1,
                self.mud_vitality
                - (self.bacteria_hunger / -self.getMaxHunger(recipe))
                * VITALITY_HUNGER_REDUCE_MAX,
            )
        thickness_overflow = self.getThickness() - recipe.max_thickness
        if thickness_overflow > 0:
            self.mud_vitality = max(
                -1,
                self.mud_vitality
                - thickness_overflow * THICKNESS_OVERFLOW_VITALITY_REDUCE,
            )

    def updateTemperature(self):
        if self.mud_temperature < 25:
            self.mud_temperature += 0.02
        elif self.mud_temperature > 30:
            self.mud_temperature -= 0.02

    def getMaxHunger(self, recipe):
        # type: (FermenterRecipe) -> float
        return recipe.nutrition_value * self.mud_volume

    def getHungerReduceRate(self, recipe):
        # type: (FermenterRecipe) -> float
        return recipe.hunger_reduce_speed * self.mud_volume

    def getGrowSpeed(self, recipe):
        # type: (FermenterRecipe) -> float
        return recipe.max_grow_speed * self.water_volume * self.mud_vitality

    def getProduceSpeed(self, recipe):
        # type: (FermenterRecipe) -> float
        thickness = self.getThickness()
        if thickness < recipe.produce_thickness:
            return 0
        if thickness < recipe.fit_thickness:
            value = 1 - (recipe.fit_thickness - thickness) / (
                recipe.fit_thickness - recipe.produce_thickness
            )
        else:
            value = 1
        return max(0, value * self.mud_vitality)

    def getGasProduceRate(self, recipe):
        # type: (FermenterRecipe) -> float
        return recipe.out_gas_rate * self.mud_volume * self.getProduceSpeed(recipe)

    def getFluidProduceRate(self, recipe):
        # type: (FermenterRecipe) -> float
        return recipe.out_fluid_rate * self.mud_volume * self.getProduceSpeed(recipe)

    def getVolume(self):
        return self.mud_volume + self.water_volume

    def getThickness(self):
        return float(self.mud_volume) / (self.getVolume() or 1)

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

    @property
    def mud_vitality(self):
        # type: () -> float
        return self.bdata[K_MUD_VITALITY] or 0.0

    @mud_vitality.setter
    def mud_vitality(self, value):
        # type: (float) -> None
        self.bdata[K_MUD_VITALITY] = value

    @property
    def mud_volume(self):
        # type: () -> float
        return self.bdata[K_MUD_VOLUME] or 0.0

    @mud_volume.setter
    def mud_volume(self, value):
        # type: (float) -> None
        self.bdata[K_MUD_VOLUME] = value

    @property
    def water_volume(self):
        # type: () -> float
        return self.bdata[K_WATER_VOLUME] or 0.0

    @water_volume.setter
    def water_volume(self, value):
        # type: (float) -> None
        self.bdata[K_WATER_VOLUME] = value

    @property
    def bacteria_hunger(self):
        # type: () -> float
        return self.bdata[K_CELL_HUNGER] or 0.0

    @bacteria_hunger.setter
    def bacteria_hunger(self, value):
        # type: (float) -> None
        self.bdata[K_CELL_HUNGER] = value

    @property
    def expected_mud_temperature(self):
        # type: () -> float
        return self.bdata[K_EXPECTED_TEMPERTURE] or 25.0

    @expected_mud_temperature.setter
    def expected_mud_temperature(self, value):
        # type: (float) -> None
        self.bdata[K_EXPECTED_TEMPERTURE] = value

    @property
    def expected_water_max_volume(self):
        # type: () -> float
        return self.bdata[K_EXPECTED_WATER_MAX_VOLUME] or POOL_MAX_VOLUME * 0.4

    @expected_water_max_volume.setter
    def expected_water_max_volume(self, value):
        # type: (float) -> None
        self.bdata[K_EXPECTED_WATER_MAX_VOLUME] = value

    @property
    def recipe_id(self):
        # type: () -> int
        return self.bdata[K_RECIPE] or 0

    @recipe_id.setter
    def recipe_id(self, value):
        # type: (int) -> None
        self.bdata[K_RECIPE] = value

    @property
    def current_inoculating_recipe(self):
        # type: () -> int
        return self.bdata[K_INOCULATING_RECIPE] or 0

    @current_inoculating_recipe.setter
    def current_inoculating_recipe(self, value):
        # type: (int) -> None
        self.bdata[K_INOCULATING_RECIPE] = value

    @property
    def current_inoculate_time(self):
        # type: () -> float
        return self.bdata[K_INOCULATE_TIME] or 0.0

    @current_inoculate_time.setter
    def current_inoculate_time(self, value):
        # type: (float) -> None
        self.bdata[K_INOCULATE_TIME] = value

    @property
    def mud_temperature(self):
        # type: () -> float
        return self.bdata[K_TEMPERATURE] or 25.0

    @mud_temperature.setter
    def mud_temperature(self, value):
        # type: (float) -> None
        self.bdata[K_TEMPERATURE] = value


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


@FermenterSeMaxVolumeEvent.Listen()
def onFermenterSeMaxVolumeEvent(event):
    # type: (FermenterSeMaxVolumeEvent) -> None
    global Fermenter
    m = SafeGetMachine(event.x, event.y, event.z, event.player_id)
    if not isinstance(m, Fermenter):
        return
    if not isinstance(event.volume, float):
        return
    m.setExpectedWaterMaxVolume(event.volume)
