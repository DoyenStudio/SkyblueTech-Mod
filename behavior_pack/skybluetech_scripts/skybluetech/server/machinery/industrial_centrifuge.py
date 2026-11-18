# coding=utf-8
import math
from copy import copy

from skybluetech_scripts.tooldelta.extensions.facing_utils import RelativeFacingStrEnum
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID

from ...common.define import flags
from ...common.define.facing import RelFacEnum
from ...common.define.id_enum import Machinery
from ...common.machinery_def.industrial_centrifuge import (
    CALCIUM_CRYSTALLIZATION, FLUID_SLOT_MAX_VOLUMES, K_BATCH_FLUID, K_WORKING,
    STORE_RF_MAX, recipes,
)
from ...common.mini_jei.core import CategoryType
from .basic import BaseClicker, HeatCtrl, MultiFluidContainer, Processor
from .basic.fluid_output_faces import FluidOutputFaces
from .basic.slot_reads import accepts_slot_reads
from .core import RegisterMachine

BASE = Machinery.INDUSTRIAL_CENTRIFUGE
TOP = Machinery.INDUSTRIAL_CENTRIFUGE_UPSIDE
AIR = {"name": "minecraft:air", "aux": 0}
_removing = set()

# 第一小批只出水。沿用同一配方的输入、工时和热耗，第二小批再结晶。
_FIRST_CRYSTALLIZATION = copy(CALCIUM_CRYSTALLIZATION)
_FIRST_CRYSTALLIZATION.outputs = {CategoryType.FLUID: CALCIUM_CRYSTALLIZATION.outputs[CategoryType.FLUID]}
_K_HALF_CRYSTAL = "centrifugeHalfCrystal"


def _remove_partner(machine, upper):
    info = CF.CreateBlockInfo(LEVEL_ID)
    x, y, z = machine.xyz
    base = (x, y - 1 if upper else y, z)
    key = (machine.dim, base)
    other = base if upper else (x, y + 1, z)
    expected = BASE if upper else TOP
    if key in _removing or (info.GetBlockNew(other, machine.dim) or {}).get("name") != expected:
        return
    _removing.add(key)
    try:
        # 拆上层时由下层原生容器掉出机体和库存；清理上层时直接替换。
        info.SetBlockNew(other, AIR, 1 if upper else 0, machine.dim)
    finally:
        _removing.discard(key)


@RegisterMachine
class IndustrialCentrifuge(FluidOutputFaces, Processor, MultiFluidContainer, HeatCtrl):
    block_name = BASE
    recipes = recipes
    store_rf_max = STORE_RF_MAX
    process_item = process_fluid = True
    item_input_slots = ()
    item_output_slots = (0,)
    upgrade_slot_start = 1
    upgrade_slots = 4
    fluid_input_slots = (0,)
    fluid_output_slots = (1, 2)
    fluid_output_slots_by_face = {
        RelativeFacingStrEnum.LEFT: (1,), RelativeFacingStrEnum.RIGHT: (2,),
    }
    fluid_slot_max_volumes = FLUID_SLOT_MAX_VOLUMES
    fluid_io_mode = (-1,) * 6
    heat_input_faces = (RelFacEnum.DOWN,)
    heat_output_faces = ()

    def __init__(self, dim, x, y, z, block_entity_data):
        FluidOutputFaces.__init__(self, dim, x, y, z, block_entity_data)
        self._working = None
        self._record_batch()
        self.handler.SubscribeOnPlaced(self._place_top)
        self.handler.SubscribeOnDestroy(self._remove_top)

    def _record_batch(self):
        recipe = self.current_recipe
        feed = recipe.inputs[CategoryType.FLUID][0].id if recipe else ""
        if self.bdata[K_BATCH_FLUID] != feed:
            self.ResetProgress()
            self.bdata[K_BATCH_FLUID] = feed

    def start_next(self, _recipe=None, check_power=True):
        Processor.start_next(self, _recipe, check_power)
        self._record_batch()

    @accepts_slot_reads
    def get_recipe(self, slot_reads=None):
        index, recipe = Processor.get_recipe(self, slot_reads)
        if recipe is CALCIUM_CRYSTALLIZATION and not self.bdata[_K_HALF_CRYSTAL]:
            recipe = _FIRST_CRYSTALLIZATION
        return index, recipe

    @accepts_slot_reads
    def finish_recipe(self, recipe, slot_reads=None):
        if not Processor.finish_recipe(self, recipe, slot_reads):
            return False
        if recipe is _FIRST_CRYSTALLIZATION or recipe is CALCIUM_CRYSTALLIZATION:
            self.bdata[_K_HALF_CRYSTAL] = recipe is _FIRST_CRYSTALLIZATION
        return True

    @classmethod
    def OnPrePlaced(cls, event):
        if not CF.CreateBlockInfo(LEVEL_ID).MayPlace(
            TOP, (event.x, event.y + 1, event.z), event.face, event.dimensionId
        ):
            event.cancel()

    def _place_top(self, event):
        info = CF.CreateBlockInfo(LEVEL_ID)
        top = (self.x, self.y + 1, self.z)
        block = info.GetBlockNew(top, self.dim) or {}
        if block.get("name") == TOP:
            return
        states = CF.CreateBlockState(LEVEL_ID)
        facing = (states.GetBlockStates(self.xyz, self.dim) or {}).get("minecraft:cardinal_direction", "north")
        aux = states.GetBlockAuxValueFromStates(TOP, {"minecraft:cardinal_direction": facing})
        if info.MayPlace(TOP, top, 1, self.dim) and info.SetBlockNew(
            top, {"name": TOP, "aux": aux}, 0, self.dim, True
        ):
            return
        info.SetBlockNew(self.xyz, AIR, 1, self.dim)

    def _remove_top(self):
        _remove_partner(self, False)

    def _processor_on_ticking(self):
        recipe = self.current_recipe
        self._advanced = False
        if recipe:
            factor = 1.0
            if recipe.heat_cost:
                factor = min(1.0, max(0.0, (self.kelvin - recipe.min_temperature)
                                       / float(recipe.fit_temperature - recipe.min_temperature)))
            self.UpdateDeactiveFlag(flags.DEACTIVE_FLAG_HEAT_LACK, factor == 0)
            self._step = min(self.ticks_left, self.reduce_ticks * factor)
            # 按累计加工量取整之差扣电，慢速运行与读档都不会逐 tick 舍入增费。
            done = recipe.tick_duration - self.ticks_left
            unit_cost = recipe.power_cost * self._power_cost_relative / self.reduce_ticks
            self._charge = int(math.ceil((done + self._step) * unit_cost)
                               - math.ceil(done * unit_cost))
            self.UpdateDeactiveFlag(flags.DEACTIVE_FLAG_POWER_LACK, self.store_rf < self._charge)
        else:
            self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_HEAT_LACK)
        Processor._processor_on_ticking(self)
        if self._advanced != self._working:
            self.bdata[K_WORKING] = self._working = self._advanced

    def ProcessOnce(self):
        recipe = self.current_recipe
        self.ReducePower(self._charge, bypass_upgraders=True)
        if recipe.heat_cost:
            self.heat_value -= recipe.heat_cost * self._step / recipe.tick_duration
        self.ticks_left -= self._step
        self._advanced = self._step > 0
        return self.ticks_left <= 0


@RegisterMachine
class IndustrialCentrifugeUpside(BaseClicker):
    block_name = TOP
    is_non_energy_machine = True
    energy_io_mode = (2,) * 6

    def __init__(self, dim, x, y, z, block_entity_data):
        BaseClicker.__init__(self, dim, x, y, z, block_entity_data)
        self.handler.SubscribeOnClick(self._open_base)
        self.handler.SubscribeOnDestroy(self._remove_base)

    @classmethod
    def OnPrePlaced(cls, event):
        event.cancel()

    def _open_base(self, event, extra_datas=None):
        base = (self.x, self.y - 1, self.z)
        if (CF.CreateBlockInfo(LEVEL_ID).GetBlockNew(base, self.dim) or {}).get("name") == BASE:
            CF.CreateBlockInfo(event.playerId).PlayerUseItemToPos(base, 2)

    def _remove_base(self):
        _remove_partner(self, True)
