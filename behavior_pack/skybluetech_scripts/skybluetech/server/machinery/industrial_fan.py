# coding=utf-8
from math import ceil

from mod.server.extraServerApi import GetMinecraftEnum
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID

from ...common.define import flags
from ...common.define.facing import (
    FACING_DIRECTION_TO_DXYZ,
    FACING_EN2NUM,
    OPPOSITE_FACING,
)
from ...common.define.id_enum import Machinery
from ...common.machinery_def.industrial_fan import (
    K_ANIM_SPEED,
    K_REDSTONE_STRENGTH,
    MAX_REDSTONE_STRENGTH,
    POWER_PER_LEVEL,
    STORE_RF_MAX,
    TICKS_PER_SECOND,
    get_wind_range,
)
from .basic import BaseMachine
from .core import RegisterMachine

EntityType = GetMinecraftEnum().EntityType
solid_blocks = {}  # type: dict[str, bool]


@RegisterMachine
class IndustrialFan(BaseMachine):
    block_name = Machinery.INDUSTRIAL_FAN
    store_rf_max = STORE_RF_MAX
    energy_io_mode = (2, 2, 2, 2, 2, 2)

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
            # ToolDelta keeps the mutable engine event in _orig.
            event.auxData = event._orig["auxData"] = aux

    def __init__(self, dim, x, y, z, block_entity_data):
        super(IndustrialFan, self).__init__(dim, x, y, z, block_entity_data)
        states = CF.CreateBlockState(LEVEL_ID).GetBlockStates(self.xyz, self.dim)
        if states is None:
            raise ValueError("IndustrialFan BlockState None")
        self.facing = states["minecraft:facing_direction"]
        self.direction = FACING_DIRECTION_TO_DXYZ[self.facing]
        self.axis = next(i for i, value in enumerate(self.direction) if value)
        back_face = OPPOSITE_FACING[FACING_EN2NUM[self.facing]]
        self.energy_io_mode = tuple(0 if face == back_face else 2 for face in range(6))
        self._anim_speed = self.bdata[K_ANIM_SPEED]
        strength = CF.CreateRedStone(LEVEL_ID).GetStrength(self.xyz, self.dim)
        if strength is None:
            strength = self.bdata[K_REDSTONE_STRENGTH] or 0
        self._set_strength(strength)
        self._set_anim_speed(0)
        self.handler.SubscribeOnTicking(self._industrial_fan_on_ticking)
        self.handler.SubscribeOnBlockRedstoneStrengthChanged(
            self._industrial_fan_on_redstone_changed
        )

    def _set_strength(self, strength):
        self.redstone_strength = max(0, min(MAX_REDSTONE_STRENGTH, int(strength)))
        if self.bdata[K_REDSTONE_STRENGTH] != self.redstone_strength:
            self.bdata[K_REDSTONE_STRENGTH] = self.redstone_strength
        self.running_power = self.redstone_strength * POWER_PER_LEVEL
        self.UpdateDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT, self.redstone_strength == 0)
        if self.redstone_strength == 0:
            self._set_anim_speed(0)

    def _industrial_fan_on_redstone_changed(self, event):
        self._set_strength(event.newStrength)

    def _set_anim_speed(self, speed):
        if speed != self._anim_speed:
            self._anim_speed = self.bdata[K_ANIM_SPEED] = speed

    def _industrial_fan_on_ticking(self):
        strength = self.redstone_strength
        power_lack = strength > 0 and self.store_rf < self.running_power
        self.UpdateDeactiveFlag(flags.DEACTIVE_FLAG_POWER_LACK, power_lack)
        if strength == 0 or not self.IsActive():
            self._set_anim_speed(0)
            return
        self.ReducePower(self.running_power)
        self._set_anim_speed(strength)
        self._blow_entities(strength)

    def _wind_bounds(self, strength):
        lower = list(self.xyz)
        upper = [value + 1 for value in self.xyz]
        wind_range = self._unblocked_wind_range(get_wind_range(strength))
        if self.direction[self.axis] > 0:
            lower[self.axis] += 1
            upper[self.axis] += wind_range
        else:
            lower[self.axis] -= wind_range
            upper[self.axis] -= 1
        return lower, upper

    def _unblocked_wind_range(self, wind_range):
        block_info = CF.CreateBlockInfo(LEVEL_ID)
        dx, dy, dz = self.direction
        for step in range(1, int(ceil(wind_range)) + 1):
            pos = (self.x + dx * step, self.y + dy * step, self.z + dz * step)
            block = block_info.GetBlockNew(pos, self.dim)
            # Do not blow through an unloaded part of the duct.
            if block is None:
                return float(step - 1)
            name = block["name"]
            if name not in solid_blocks:
                info = block_info.GetBlockBasicInfo(name)
                if not info or "solid" not in info:
                    return float(step - 1)
                solid_blocks[name] = bool(info["solid"])
            if solid_blocks[name]:
                return float(step - 1)
        return wind_range

    def _blow_entities(self, strength):
        lower, upper = self._wind_bounds(strength)
        if lower[self.axis] >= upper[self.axis]:
            return
        # In-game verification confirms float bounds and collision-box overlap,
        # preserving the linear range and catching bodies crossing the duct.
        entities = CF.CreateGame(LEVEL_ID).GetEntitiesInSquareArea(
            None, tuple(lower), tuple(upper), self.dim,
        ) or []
        speed = self.direction[self.axis] * strength / TICKS_PER_SECOND
        for entity_id in entities:
            entity_type = CF.CreateEngineType(entity_id).GetEngineType()
            if entity_type is None:
                continue
            type_id = entity_type & EntityType.TypeMask
            if type_id != EntityType.ItemEntity and not (entity_type & EntityType.Mob):
                continue
            motion_comp = CF.CreateActorMotion(entity_id)
            motion = motion_comp.GetMotion()
            if motion is None:
                continue
            motion = list(motion)
            motion[self.axis] = speed
            if type_id == (EntityType.Player & EntityType.TypeMask):
                motion_comp.SetPlayerMotion(tuple(motion))
            else:
                motion_comp.SetMotion(tuple(motion))
