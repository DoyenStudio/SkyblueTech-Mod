# coding=utf-8
from random import uniform
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.extensions.facing_utils import (
    get_absolute_facing_by_facing_direction,
)
from skybluetech_scripts.tooldelta.extensions.entity_utils_server import (
    GetOnlinePlayers,
    GetEntityDimension,
    GetEntityPosition,
)

from ...common.define.facing import FACING_DIRECTION_TO_DXYZ, FACING_EN2NUM
from ...common.define.id_enum import Machinery
from ...common.events.machinery.shocker import ShockerCoilSpark
from ...common.machinery_def.shocker import MAX_GAP, MIN_GAP, STORE_RF_MAX
from .basic import BaseMachine
from .core import RegisterMachine
from .core.pool import GetLoadedMachine
from .utils.shocker_pair import ShockerPair


def GetBlock(pos, dim):
    return CF.CreateBlockInfo(LEVEL_ID).GetBlockNew(pos, dim)


def GetBlockStates(pos, dim):
    return CF.CreateBlockState(LEVEL_ID).GetBlockStates(pos, dim)


def GetBlockSolid(name):
    info = CF.CreateBlockInfo(LEVEL_ID).GetBlockBasicInfo(name)
    if info is None or "solid" not in info:
        return None
    return bool(info["solid"])


def GetRedstoneStrength(pos, dim):
    return CF.CreateRedStone(LEVEL_ID).GetStrength(pos, dim)


@RegisterMachine
class Shocker(BaseMachine):
    block_name = Machinery.SHOCKER
    store_rf_max = STORE_RF_MAX
    energy_io_mode = (2, 2, 2, 2, 2, 2)

    def __init__(self, dim, x, y, z, block_entity_data):
        super(Shocker, self).__init__(dim, x, y, z, block_entity_data)
        self.facing = None
        self.direction = None
        self.pair = None
        self.loaded = True
        self.redstone_strength = GetRedstoneStrength(self.xyz, self.dim) or 0
        self.refresh_facing()
        self.handler.SubscribeOnTicking(self._on_ticking)
        self.handler.SubscribeOnBlockRandomTick(self._on_random_tick)
        self.handler.SubscribeOnBlockRedstoneStrengthChanged(self._on_redstone_changed)
        self.handler.SubscribeOnUnload(self._on_unload)

    def refresh_facing(self):
        states = GetBlockStates(self.xyz, self.dim)
        facing = states.get("minecraft:facing_direction") if states else None
        if facing not in FACING_DIRECTION_TO_DXYZ:
            return False
        if facing != self.facing:
            self.facing = facing
            self.direction = FACING_DIRECTION_TO_DXYZ[facing]
            inputs = set(FACING_EN2NUM[get_absolute_facing_by_facing_direction(
                facing, relative_face
            )] for relative_face in ("back", "top"))
            self.energy_io_mode = tuple(0 if face in inputs else 2 for face in range(6))
        return True

    def find_partner(self):
        if not self.loaded or not self.refresh_facing():
            return None
        for step in range(1, MAX_GAP + 2):
            pos = tuple(value + delta * step for value, delta in zip(self.xyz, self.direction))
            block = GetBlock(pos, self.dim)
            if block is None:
                return None
            name = block.get("name")
            if name == self.block_name:
                partner = GetLoadedMachine(self.dim, *pos)
                if (step - 1 >= MIN_GAP and isinstance(partner, Shocker)
                        and partner.loaded and partner.refresh_facing()
                        and partner.direction == tuple(-value for value in self.direction)):
                    return partner
                return None
            if not name or GetBlockSolid(name) is not False:
                return None
        return None

    def _ensure_pair(self):
        if self.pair is not None:
            return self.pair
        partner = self.find_partner()
        if partner is None:
            return None
        if partner.pair is not None:
            if partner.pair.is_valid():
                return None
            partner.pair.close()
        first, second = sorted((self, partner), key=lambda machine: machine.xyz)
        pair = ShockerPair(first, second)
        pair.start()
        return self.pair

    def _on_ticking(self):
        if self.pair is not None and self.pair.first is self:
            if not self.pair.is_valid():
                self.pair.close()
        if self.pair is None:
            self._ensure_pair()

    def _on_redstone_changed(self, event):
        self.redstone_strength = event.newStrength
        if self.pair is not None and not self.pair.is_valid():
            self.pair.close()
        pair = self._ensure_pair()
        if pair is not None and event.oldStrength == 0 and event.newStrength > 0:
            pair.request_pulse()

    def _on_random_tick(self, _event):
        if not self.loaded or self.store_rf <= 0 or not self.refresh_facing():
            return
        players = []
        for player_id in GetOnlinePlayers():
            if GetEntityDimension(player_id) != self.dim:
                continue
            pos = GetEntityPosition(player_id)
            if pos is not None and sum((a - (b + 0.5)) ** 2
                                       for a, b in zip(pos, self.xyz)) <= 32 ** 2:
                players.append(player_id)
        if not players:
            return
        axes = [FACING_DIRECTION_TO_DXYZ[get_absolute_facing_by_facing_direction(
            self.facing, face)] for face in ("right", "top", "front")]
        points = []
        for _ in range(3):
            # Model pixels: x/z in [-2, 2], y in [6, 16], about block centre.
            offsets = (uniform(-2, 2) / 16.0, uniform(-2, 8) / 16.0,
                       uniform(-2, 2) / 16.0)
            points.append(tuple(self.xyz[i] + 0.5 + sum(
                axes[j][i] * offsets[j] for j in range(3)) for i in range(3)))
        ShockerCoilSpark(self.dim, self.xyz, points).sendMulti(players)

    def _on_unload(self):
        self.loaded = False
        if self.pair is not None:
            self.pair.close()
