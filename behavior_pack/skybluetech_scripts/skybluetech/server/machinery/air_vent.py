# coding=utf-8
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.extensions.facing_utils import RelativeFacingStrEnum

from ...common.define.facing import FACING_EN2NUM, OPPOSITE_FACING
from ...common.define.id_enum import Machinery
from ...common.define.id_enum.fluids import ChemicalGas, CommonGas
from ...common.events.machinery.air_vent import AirVentExhaust
from ...common.machinery_def.air_vent import (
    MAX_FLUID_VOLUME, TICK_INTERVAL, FLUID_PER_CYCLE,
)
from .basic import MultiFluidContainer
from .core import RegisterMachine


@RegisterMachine
class AirVent(MultiFluidContainer):
    block_name = Machinery.AIR_VENT
    is_non_energy_machine = True
    store_rf_max = 0
    energy_io_mode = (2, 2, 2, 2, 2, 2)
    fluid_input_slots = (0,)
    fluid_output_slots = ()
    fluid_slot_max_volumes = {0: MAX_FLUID_VOLUME}
    fluid_input_slots_by_face = {RelativeFacingStrEnum.BACK: (0,)}
    fluid_output_slots_by_face = {}
    allow_player_use_bucket_interact = False
    allow_player_use_bucket_push = False
    allow_player_use_bucket_pull = False

    @classmethod
    def OnPrePlaced(cls, event):
        block_state = CF.CreateBlockState(LEVEL_ID)
        states = block_state.GetBlockStatesFromAuxValue(cls.block_name, event.auxData)
        if states is None:
            return
        facing = states.get("minecraft:facing_direction")
        if facing not in ("up", "down"):
            return
        states["minecraft:facing_direction"] = "down" if facing == "up" else "up"
        aux = block_state.GetBlockAuxValueFromStates(cls.block_name, states)
        if aux is not None:
            event.auxData = event._orig["auxData"] = aux

    def __init__(self, dim, x, y, z, block_entity_data):
        super(AirVent, self).__init__(dim, x, y, z, block_entity_data)
        self._ticks = 0
        self.handler.SubscribeOnTicking(self._air_vent_on_ticking)
        self.handler.SubscribeOnInvalidateCaches(self._update_facing)
        self._update_facing()

    def _update_facing(self):
        states = CF.CreateBlockState(LEVEL_ID).GetBlockStates(self.xyz, self.dim) or {}
        self.facing = FACING_EN2NUM.get(states.get("minecraft:facing_direction"))
        back = OPPOSITE_FACING[self.facing] if self.facing is not None else None
        self.fluid_io_mode = tuple(0 if face == back else 2 for face in range(6))

    def IsValidFluidInput(self, slot, fluid_id):
        return slot == 0 and (
            fluid_id in CommonGas.all_sub()
            or fluid_id == ChemicalGas.CARBON_DIOXIDE
        )

    def _air_vent_on_ticking(self):
        self._ticks += 1
        if self._ticks < TICK_INTERVAL:
            return
        self._ticks = 0
        fluid = self.fluids[0]
        if self.facing is None or fluid.volume <= 0:
            return
        fluid_id = fluid.fluid_id
        volume = min(FLUID_PER_CYCLE, fluid.volume)
        fluid.volume -= volume
        self._on_reduced_fluid(0, fluid_id, volume, True)
        AirVentExhaust(self.dim, self.xyz, self.facing, fluid_id, volume).sendAll()
