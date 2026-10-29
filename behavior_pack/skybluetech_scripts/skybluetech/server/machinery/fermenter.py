# coding=utf-8
from skybluetech_scripts.tooldelta.define.item import Item

from .basic.item_container import ItemContainer
from ...common.define import flags
from ...common.define.id_enum import Machinery
from ...common.define.id_enum.multi_block_structure import Fermenter as FERMENTER_IDENUM
from ...common.events.machinery.fermenter import (
    FermenterSeMaxVolumeEvent,
    FermenterSetTemperatureEvent,
)
from ...common.machinery_def.fermenter import (
    HI_TEMPERATURE_VITALITY_REDUCE,
    K_CELL_HUNGER,
    K_EXPECTED_TEMPERTURE,
    K_EXPECTED_WATER_MAX_VOLUME,
    K_FLUID_PRODUCE_SPEED,
    K_GAS_PRODUCE_SPEED,
    K_INOCULATE_TIME,
    K_INOCULATING_RECIPE,
    K_MUD_THICKNESS,
    K_MUD_VITALITY,
    K_MUD_VOLUME,
    K_OUTPUT_FLUID_ID,
    K_OUTPUT_FLUID_MAX_VOLUME,
    K_OUTPUT_FLUID_VOLUME,
    K_OUTPUT_GAS_ID,
    K_OUTPUT_GAS_MAX_VOLUME,
    K_OUTPUT_GAS_VOLUME,
    K_RECIPE,
    K_TEMPERATURE,
    K_TOTAL_VOLUME,
    K_WATER_VOLUME,
    POOL_MAX_VOLUME,
    STORE_RF_MAX,
    STRUCTURE_PALETTE,
    TEMPERATURE_MAX,
    TEMPERATURE_MIN,
    THICKNESS_OVERFLOW_VITALITY_REDUCE,
    VITALITY_ADD_MAX,
    VITALITY_HUNGER_REDUCE_MAX,
    FermenterRecipe,
    spec_recipes,
)
from .basic import (
    GUIControl,
    MultiBlockStructure,
    OperationListener,
    UpgradeControl,
    WorkRenderer,
)
from .core import RegisterMachine
from .interfaces import (
    EnergyInputInterface,
    FluidInputInterface,
    FluidOutputInterface,
    ItemInputInterface,
)

EnergyInputInterface.AddExtraMachineId(FERMENTER_IDENUM.IO_ENERGY)
FluidInputInterface.AddExtraMachineId(FERMENTER_IDENUM.IO_FLUID1)
FluidOutputInterface.AddExtraMachineId(FERMENTER_IDENUM.IO_FLUID2)
FluidOutputInterface.AddExtraMachineId(FERMENTER_IDENUM.IO_GAS)
ItemInputInterface.AddExtraMachineId(FERMENTER_IDENUM.IO_ITEM)


@RegisterMachine
class Fermenter(
    OperationListener,
    WorkRenderer,
    UpgradeControl,
    MultiBlockStructure,
    GUIControl,
):
    block_name = Machinery.FERMENTER
    store_rf_max = STORE_RF_MAX
    origin_process_ticks = 1
    running_power = 5
    structure_palette = STRUCTURE_PALETTE
    item_input_slots = (0, 1)
    fluid_io_mode = (2, 2, 2, 2, 2, 2)
    fluid_input_slots = (0,)
    fluid_output_slots = (1, 2)
    fluid_slot_max_volumes = {0: 1000, 1: 1000, 2: 1000}
    work_ticks_delay = 5
    upgrade_slot_start = 2
    allow_upgraders = frozenset()
    functional_block_ids = {
        FERMENTER_IDENUM.IO_ENERGY,
        FERMENTER_IDENUM.IO_ITEM,
        FERMENTER_IDENUM.IO_FLUID1,
        FERMENTER_IDENUM.IO_FLUID2,
        FERMENTER_IDENUM.IO_GAS,
    }

    def __init__(self, dim, x, y, z, block_entity_data):
        super(Fermenter, self).__init__(dim, x, y, z, block_entity_data)
        self.t = 0
        self._energy_in = None
        self._item_in = None
        self._water_in = None
        self._fluid_out = None
        self._gas_out = None
        self.handler.SubscribeOnTicking(self._fermenter_on_ticking)
        self.handler.SubscribeOnStructureChanged(self._fermenter_on_structure_changed)
        self.handler.SubscribeOnUnload(self._fermenter_on_unload)
        self.handler.SubscribeOnSync(self._fermenter_on_sync)
        self.handler.SubscribeOnSlotUpdate(self._fermenter_on_slot_update)
        self.CallSync()

    def _fermenter_on_ticking(self):
        self.t += 1
        if self.t >= self.work_ticks_delay:
            self.t = 0
            if not self.StructureFinished():
                return
            # 未接种菌种 (也不在接种中) 时没有产出, 状态灯显示待机。这个标志只用于显示:
            # 下面加水 / 控温 / 接种 / 生长的判断都忽略它, 否则永远等不到接种
            self.UpdateDeactiveFlag(
                flags.DEACTIVE_FLAG_NO_RECIPE,
                self.recipe_id == 0 and self.current_inoculating_recipe == 0,
            )
            if self.IsActiveIgnoreCondition(flags.DEACTIVE_FLAG_NO_RECIPE):
                if self.ProcessOnce():
                    self.workOnce()
                    self.CallSync()
            if self.IsActiveIgnoreCondition(flags.DEACTIVE_FLAG_POWER_LACK | flags.DEACTIVE_FLAG_NO_RECIPE):
                self.tryInoculate()
                recipe = spec_recipes.get(self.recipe_id)
                if recipe is None:
                    return
                self.lifeCycle(recipe)
                self.CallSync()

    def _fermenter_on_structure_changed(self, ok):
        # type: (bool) -> None
        if ok:
            self._energy_in = self.getEnergyInIO()
            self._item_in = self.getItemInIO()
            self._water_in = self.getWaterInIO()
            self._fluid_out = self.getFluidOutIO()
            self._gas_out = self.getGasOutIO()
            self._energy_in.SetMachineRef(self)
            self._item_in.SetMachineRef(self)
            self._water_in.SetMachineRef(self)
            self._fluid_out.SetMachineRef(self)
            self._gas_out.SetMachineRef(self)
            self._item_in.SetOnSlotUpdateCallback(self.on_other_slot_update)
        else:
            self.clean()
        self.CallSync()

    def _fermenter_on_unload(self):
        self.clean()

    def _fermenter_on_sync(self):
        self.bdata[K_MUD_THICKNESS] = self.getThickness()
        if self.StructureFinished():
            self.bdata[K_TOTAL_VOLUME] = float(self.getVolume()) / POOL_MAX_VOLUME
            gas = self.getGasOutIO().fluids[0]
            fluid = self.getFluidOutIO().fluids[0]
            self.bdata[K_OUTPUT_GAS_ID] = gas.fluid_id
            self.bdata[K_OUTPUT_GAS_VOLUME] = gas.volume
            self.bdata[K_OUTPUT_GAS_MAX_VOLUME] = gas.max_volume
            self.bdata[K_OUTPUT_FLUID_ID] = fluid.fluid_id
            self.bdata[K_OUTPUT_FLUID_VOLUME] = fluid.volume
            self.bdata[K_OUTPUT_FLUID_MAX_VOLUME] = fluid.max_volume
            if self.recipe_id > 0:
                recipe = spec_recipes[self.recipe_id]
                self.bdata[K_GAS_PRODUCE_SPEED] = self.getGasProduceRate(recipe) * (
                    20.0 / self.work_ticks_delay
                )
                self.bdata[K_FLUID_PRODUCE_SPEED] = self.getFluidProduceRate(recipe) * (
                    20.0 / self.work_ticks_delay
                )
            else:
                self.bdata[K_GAS_PRODUCE_SPEED] = 0.0
                self.bdata[K_FLUID_PRODUCE_SPEED] = 0.0
        else:
            self.bdata[K_TOTAL_VOLUME] = 0.0
            self.bdata[K_OUTPUT_GAS_ID] = None
            self.bdata[K_OUTPUT_GAS_VOLUME] = 0.0
            self.bdata[K_OUTPUT_GAS_MAX_VOLUME] = 1.0
            self.bdata[K_OUTPUT_FLUID_ID] = None
            self.bdata[K_OUTPUT_FLUID_VOLUME] = 0.0
            self.bdata[K_OUTPUT_FLUID_MAX_VOLUME] = 1.0
            self.bdata[K_GAS_PRODUCE_SPEED] = 0.0
            self.bdata[K_FLUID_PRODUCE_SPEED] = 0.0

    def _fermenter_on_slot_update(self, slot_pos):
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
        elif slot_pos == 1:
            if self.IsActiveIgnoreCondition(flags.DEACTIVE_FLAG_NO_RECIPE):
                for i in range(5):
                    self.on_other_slot_update(i)

    def on_other_slot_update(self, slot_pos):
        # type: (int) -> None
        item = self.getItemInIO().GetSlotItem(slot_pos)
        if item is None:
            return
        if self.IsValidInput(1, item) and self.GetSlotItem(1) is None:
            self.SetSlotItem(1, item)
            self.getItemInIO().SetSlotItem(slot_pos, None)

    def IsValidInput(self, slot, item):
        # type: (int, Item) -> bool
        results = (
            ItemContainer.IsValidInput(self, slot, item),
            UpgradeControl.IsValidInput(self, slot, item),
            self._fermenter_is_valid_input(slot, item),
        )
        return all(results)

    def _fermenter_is_valid_input(self, slot, item):
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


    def clean(self):
        if self._energy_in is not None:
            self._energy_in.UnsetMachineRef()
            self._energy_in = None
        if self._item_in is not None:
            self._item_in.UnsetMachineRef()
            self._item_in = None
        if self._water_in is not None:
            self._water_in.UnsetMachineRef()
            self._water_in = None
        if self._fluid_out is not None:
            self._fluid_out.UnsetMachineRef()
            self._fluid_out = None
        if self._gas_out is not None:
            self._gas_out.UnsetMachineRef()
            self._gas_out = None

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
        self.CallSync()

    def setExpectedWaterMaxVolume(self, volume):
        # type: (float) -> None
        if volume < 0 or volume > POOL_MAX_VOLUME:
            return
        self.expected_water_max_volume = volume
        self.CallSync()

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
        deficit = self.expected_water_max_volume - self.getVolume()
        if deficit <= 0:
            return
        water_in = self.getWaterInIO()
        fluid = water_in.fluids[0]
        if fluid.volume <= 0:
            return
        fluid_id = fluid.fluid_id
        add_amount = min(deficit, fluid.volume)
        fluid.volume -= add_amount
        self.water_volume += add_amount
        water_in._on_reduced_fluid(0, fluid_id, add_amount, True)

    def tryEat(self, recipe):
        # type: (FermenterRecipe) -> None
        if self.bacteria_hunger >= self.getMaxHunger(recipe):
            return
        maybe_food = self.GetSlotItem(1)
        if (
            maybe_food is None
            or maybe_food.count <= 0
            or maybe_food.id != recipe.nutrition_matter
        ):
            return
        maybe_food.count -= 1
        self.SetSlotItem(1, maybe_food)
        self.bacteria_hunger += float(recipe.nutrition_value)
        self.mud_vitality = min(
            1, self.mud_vitality + recipe.nutrition_recover_vitality
        )

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
        if grow_speed > 0:
            max_grow = POOL_MAX_VOLUME - self.getVolume()
            if max_grow > 0:
                self.mud_volume += min(grow_speed, max_grow)
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
        gas_io.OutputFluid(recipe.out_gas_id, self.getGasProduceRate(recipe), 0, True)
        fluid_io.OutputFluid(recipe.out_fluid_id, self.getFluidProduceRate(recipe), 0, True)

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
            loss_rate = 0.20 + 0.02 * (min_temp - mud_temp)
            self.mud_vitality = max(0, self.mud_vitality * (1 - loss_rate))
        elif mud_temp <= fit_temp and self.bacteria_hunger > 0:
            hunger_ratio = min(1.0, self.bacteria_hunger / self.getMaxHunger(recipe))
            self.mud_vitality = min(
                1,
                self.mud_vitality + VITALITY_ADD_MAX * hunger_ratio,
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
        return (
            recipe.max_hunger_portions
            * recipe.nutrition_value
            * self.mud_volume
            / (POOL_MAX_VOLUME * 0.625)
        )

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
        return self.GetLoadedMachine(ItemInputInterface, FERMENTER_IDENUM.IO_ITEM)

    def getEnergyInIO(self):
        return self.GetLoadedMachine(EnergyInputInterface, FERMENTER_IDENUM.IO_ENERGY)

    def getWaterInIO(self):
        return self.GetLoadedMachine(FluidInputInterface, FERMENTER_IDENUM.IO_FLUID1)

    def getFluidOutIO(self):
        return self.GetLoadedMachine(FluidOutputInterface, FERMENTER_IDENUM.IO_FLUID2)

    def getGasOutIO(self):
        return self.GetLoadedMachine(FluidOutputInterface, FERMENTER_IDENUM.IO_GAS)

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


@Fermenter.ForOperation(FermenterSetTemperatureEvent)
def onFermenterSetTemperatureEvent(event, machine):
    # type: (FermenterSetTemperatureEvent, Fermenter) -> None
    if not isinstance(event.temperature, float):
        return
    machine.setExpectedTemperature(event.temperature)


@Fermenter.ForOperation(FermenterSeMaxVolumeEvent)
def onFermenterSeMaxVolumeEvent(event, machine):
    # type: (FermenterSeMaxVolumeEvent, Fermenter) -> None
    if not isinstance(event.volume, float):
        return
    machine.setExpectedWaterMaxVolume(event.volume)
