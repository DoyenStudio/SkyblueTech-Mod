# coding=utf-8
from skybluetech_scripts.tooldelta.extensions.entity_utils_server import (
    CreateEntityRegion,
    DeleteEntityRegion,
    EntityType,
    GetEntityDimension,
    GetEntityPosition,
    GetEntityType,
    IsEntityAlive,
)
from skybluetech_scripts.tooldelta.general import ServerUninitCallback
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID

from ....common.define.id_enum import TransmitBelt
from ...machinery.basic.base_machine import BaseMachine
from ...machinery.core import RegisterMachine
from ...machinery.core.pool import GetLoadedMachine

POWERED_STATE = "skybluetech:detector_belt_powered"
REGION_RETRY_TICKS = 20
EXCLUDED_MOB_TYPES = frozenset(
    entity_type & EntityType.TypeMask
    for entity_type in (
        EntityType.ArmorStand,
        EntityType.TripodCamera,
        EntityType.Npc,
        EntityType.Agent,
    )
)
loaded_detectors = {}  # type: dict[tuple[int, int, int, int], DetectorBelt]


def _is_mob(entity_type):
    return (entity_type is not None and bool(entity_type & EntityType.Mob)
            and entity_type & EntityType.TypeMask not in EXCLUDED_MOB_TYPES)


@RegisterMachine
class DetectorBelt(BaseMachine):
    block_name = TransmitBelt.DETECTOR
    is_non_energy_machine = True
    store_rf_max = 0
    energy_io_mode = (2, 2, 2, 2, 2, 2)

    def __init__(self, dim, x, y, z, block_entity_data):
        super(DetectorBelt, self).__init__(dim, x, y, z, block_entity_data)
        self.key = (dim, x, y, z)
        previous = loaded_detectors.get(self.key)
        if previous is not None:
            previous.close()
        loaded_detectors[self.key] = self
        self.loaded = True
        self.region_name = "skybluetech:detector_belt:%d:%d:%d:%d" % self.key
        self.region_created = False
        self.region_retry_ticks = 0
        self.candidates = set()
        self.powered = None
        self.handler.SubscribeOnTicking(self._on_ticking)
        self.handler.SubscribeOnDestroy(self.close)
        self.handler.SubscribeOnUnload(self.close)

    def _is_current(self):
        return self.loaded and GetLoadedMachine(self.dim, *self.xyz) is self

    def _on_ticking(self):
        if not self._is_current():
            return
        if not self.region_created:
            if self.region_retry_ticks > 0:
                self.region_retry_ticks -= 1
            else:
                # 创建时的初始回调会补入已经站在带上的生物。
                self.region_created = CreateEntityRegion(
                    self.dim,
                    self.region_name,
                    (self.x, self.y, self.z, self.x + 1, self.y + 1, self.z + 1),
                    self._on_region_changed,
                )
                if not self.region_created:
                    self.region_retry_ticks = REGION_RETRY_TICKS
        self._refresh_output()

    def _on_region_changed(self, data):
        if not self._is_current():
            return
        entity_id = data["entityId"]
        if not data["isEnter"]:
            self.candidates.discard(entity_id)
        elif _is_mob(data["entityType"]):
            self.candidates.add(entity_id)
        self._refresh_output()

    def _refresh_output(self):
        powered = False
        for entity_id in tuple(self.candidates):
            if (not IsEntityAlive(entity_id)
                    or GetEntityDimension(entity_id) != self.dim
                    or not _is_mob(GetEntityType(entity_id))):
                self.candidates.discard(entity_id)
                continue
            pos = GetEntityPosition(entity_id)
            if pos is None:
                continue
            x, y, z = pos
            # AOI 只提供候选；脚点避免旁边生物的碰撞盒或高处生物误触发。
            if (self.x <= x < self.x + 1 and self.z <= z < self.z + 1
                    and self.y <= y <= self.y + 0.125):
                powered = True
        self._set_powered(powered)

    def _set_powered(self, powered):
        if self.powered is powered:
            return
        block_state = CF.CreateBlockState(LEVEL_ID)
        states = block_state.GetBlockStates(self.xyz, self.dim)
        if states is None or POWERED_STATE not in states:
            return
        if bool(states[POWERED_STATE]) != powered:
            states[POWERED_STATE] = powered
            if block_state.SetBlockStates(self.xyz, states, self.dim) is not True:
                return
        self.powered = powered

    def close(self):
        self.loaded = False
        if self.region_created:
            DeleteEntityRegion(self.dim, self.region_name)
            self.region_created = False
        self.candidates.clear()
        if loaded_detectors.get(self.key) is self:
            loaded_detectors.pop(self.key)


@ServerUninitCallback()
def clear_detector_regions():
    for detector in tuple(loaded_detectors.values()):
        detector.close()
