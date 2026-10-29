# coding=utf-8
from math import sqrt

from mod.server.extraServerApi import GetMinecraftEnum
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.events.server import (
    ServerBlockUseEvent,
    ServerEntityTryPlaceBlockEvent,
)

from ...common.define.id_enum import Machinery
from ...common.events.machinery.tesla_plant import (
    TeslaPlantSettingsUpload,
    TeslaPlantSettingsUpdate,
    TeslaPlantAttack,
)
from ...common.machinery_def.tesla_plant import (
    DEFAULT_WORK_RANGE,
    MIN_WORK_RANGE,
    MAX_WORK_RANGE,
    K_SETTING_ATTACK_MONSTER,
    K_SETTING_ATTACK_MOB,
    K_SETTING_ATTACK_PLAYER,
    K_SETTING_WORK_RANGE,
    SHOCK_RF,
    SHOCK_DAMAGE,
    SHOCK_INTERVAL,
    STORE_RF_MAX,
    get_shock_rf,
)
from ...common.utils.block_sync import BlockSync
from .basic import GUIControl, OperationListener, PowerControl
from .core import RegisterMachine

ActorDamageCause = GetMinecraftEnum().ActorDamageCause
EntityType = GetMinecraftEnum().EntityType
AttrType = GetMinecraftEnum().AttrType
ItemPosType = GetMinecraftEnum().ItemPosType

block_sync = BlockSync(Machinery.TESLA_PLANT, side=BlockSync.SIDE_SERVER)
_destroying_towers = set()


@RegisterMachine
class TeslaPlant(OperationListener, PowerControl, GUIControl):
    block_name = Machinery.TESLA_PLANT
    store_rf_max = STORE_RF_MAX
    running_power = SHOCK_RF

    def __init__(self, dim, x, y, z, block_entity_data):
        super(TeslaPlant, self).__init__(dim, x, y, z, block_entity_data)
        states = CF.CreateBlockState(LEVEL_ID).GetBlockStates(self.xyz, self.dim)
        if states is None:
            raise ValueError("TeslaPlant BlockState None")
        self.layer = states["skybluetech:layer"]
        self.is_base_block = self.layer == 0
        self._shock_ticks = 0
        if not self.is_base_block:
            self.energy_io_mode = (2, 2, 2, 2, 2, 2)
        else:
            self._init_settings()
            self.PowerEnough()
        self.handler.UnsubscribeOnClick(self._gui_control_on_click)
        self.handler.SubscribeOnClick(self._tesla_plant_on_click)
        self.handler.SubscribeOnPlaced(self._tesla_plant_on_placed)
        self.handler.SubscribeOnTicking(self._tesla_plant_on_ticking)
        self.handler.SubscribeOnDestroy(self._tesla_plant_on_destroy)
        self.handler.SubscribeOnUnload(self._tesla_plant_on_unload)
        self.handler.SubscribeOnSync(self._tesla_plant_on_sync)

    def _init_settings(self):
        for key, default in (
            (K_SETTING_ATTACK_MONSTER, True),
            (K_SETTING_ATTACK_MOB, False),
            (K_SETTING_ATTACK_PLAYER, False),
        ):
            if type(self.bdata[key]) is not bool:
                self.bdata[key] = default
        work_range = self.bdata[K_SETTING_WORK_RANGE]
        if type(work_range) is not int or not MIN_WORK_RANGE <= work_range <= MAX_WORK_RANGE:
            self.bdata[K_SETTING_WORK_RANGE] = DEFAULT_WORK_RANGE

    @classmethod
    def OnPrePlaced(cls, event):
        # type: (ServerEntityTryPlaceBlockEvent) -> None
        comp = CF.CreateBlockInfo(LEVEL_ID)
        for layer in (1, 2):
            if not comp.MayPlace(
                event.fullName,
                (event.x, event.y + layer, event.z),
                event.face,
                event.dimensionId,
            ):
                event.cancel()
                return

    def _tesla_plant_on_placed(self, _):
        if not self.is_base_block:
            return
        state_comp = CF.CreateBlockState(LEVEL_ID)
        for layer in (1, 2):
            aux = state_comp.GetBlockAuxValueFromStates(
                self.block_name, {"skybluetech:layer": layer}
            )
            CF.CreateBlockInfo(LEVEL_ID).SetBlockNew(
                (self.x, self.y + layer, self.z),
                {"name": self.block_name, "aux": aux},
                0,
                dimensionId=self.dim,
            )

    def _tesla_plant_on_click(self, event, extra_datas=None):
        # type: (ServerBlockUseEvent, dict | None) -> None
        if self.is_base_block:
            GUIControl._gui_control_on_click(self, event, extra_datas)
        else:
            event.cancel()
            base_pos = (self.x, self.y - self.layer, self.z)
            base_block = CF.CreateBlockInfo(LEVEL_ID).GetBlockNew(base_pos, self.dim) or {}
            base_states = CF.CreateBlockState(LEVEL_ID).GetBlockStates(base_pos, self.dim) or {}
            if (
                base_block.get("name") != self.block_name
                or base_states.get("skybluetech:layer") != 0
            ):
                return
            CF.CreateBlockInfo(event.playerId).PlayerUseItemToPos(
                base_pos, ItemPosType.CARRIED, 0, event.face
            )

    def _tesla_plant_on_destroy(self):
        base_y = self.y - self.layer
        tower_pos = (self.dim, self.x, base_y, self.z)
        if tower_pos in _destroying_towers:
            return
        _destroying_towers.add(tower_pos)
        try:
            block_comp = CF.CreateBlockInfo(LEVEL_ID)
            state_comp = CF.CreateBlockState(LEVEL_ID)
            for layer in (0, 1, 2):
                if layer == self.layer:
                    continue
                pos = (self.x, base_y + layer, self.z)
                if (block_comp.GetBlockNew(pos, self.dim) or {}).get("name") != self.block_name:
                    continue
                states = state_comp.GetBlockStates(pos, self.dim)
                if states is not None and states.get("skybluetech:layer") == layer:
                    block_comp.SetBlockNew(
                        pos, {"name": "minecraft:air", "aux": 0},
                        0, dimensionId=self.dim,
                    )
        finally:
            _destroying_towers.discard(tower_pos)

    def _tesla_plant_on_unload(self):
        block_sync.discard_block((self.dim, self.x, self.y, self.z))

    def _tesla_plant_on_sync(self):
        if self.is_base_block:
            self.get_settings_update().sendMulti(self.ui_sync.GetPlayersInSync())

    def _structure_finished(self):
        block_comp = CF.CreateBlockInfo(LEVEL_ID)
        state_comp = CF.CreateBlockState(LEVEL_ID)
        for layer in (1, 2):
            pos = (self.x, self.y + layer, self.z)
            if (block_comp.GetBlockNew(pos, self.dim) or {}).get("name") != self.block_name:
                return False
            states = state_comp.GetBlockStates(pos, self.dim)
            if states is None or states.get("skybluetech:layer") != layer:
                return False
        return True

    def _tesla_plant_on_ticking(self):
        if not self.is_base_block:
            return
        # ServerBlockEntityTickEvent is documented as 20 ticks per second.
        self._shock_ticks += 1
        if self._shock_ticks < int(SHOCK_INTERVAL * 20):
            return
        self._shock_ticks = 0
        if not self.PowerEnough() or not self.IsActive() or not self._structure_finished():
            return
        self.work_once()

    def work_once(self):
        work_range = self.work_range
        # Broad integer query, followed by an exact position check against the
        # same tower-top-centred box displayed by the range preview.
        entities = CF.CreateGame(LEVEL_ID).GetEntitiesInSquareArea(
            None,
            (self.x - work_range, self.y + 2 - work_range, self.z - work_range),
            (self.x + work_range + 1, self.y + work_range + 3, self.z + work_range + 1),
            self.dim,
        ) or []
        self.attack_once(entities)

    def _target_enabled(self, entity_type):
        # EntityType.Monster contains PathfinderMob/Mob bits, and Player
        # contains the Mob bit; non-zero masks would match the wrong group.
        type_id = entity_type & EntityType.TypeMask
        if type_id == (EntityType.Player & EntityType.TypeMask):
            return self.do_attack_player
        if (entity_type & EntityType.Monster) == EntityType.Monster:
            return self.do_attack_monster
        if not (entity_type & EntityType.Mob):
            return False
        if type_id in (
            EntityType.ArmorStand & EntityType.TypeMask,
            EntityType.TripodCamera & EntityType.TypeMask,
            EntityType.Npc & EntityType.TypeMask,
            EntityType.Agent & EntityType.TypeMask,
        ):
            return False
        return self.do_attack_mob

    def attack_once(self, entities):
        # type: (list[str]) -> None
        hit_ids = []
        hit_positions = []
        centre = (self.x + 0.5, self.y + 2.5, self.z + 0.5)
        work_range = self.work_range
        owner = self.GetOwner()
        targets = []
        seen = set()
        for entity_id in entities:
            if entity_id == owner or entity_id in seen:
                continue
            seen.add(entity_id)
            entity_type = CF.CreateEngineType(entity_id).GetEngineType()
            if entity_type is None or not self._target_enabled(entity_type):
                continue
            health = CF.CreateAttr(entity_id).GetAttrValue(AttrType.HEALTH)
            if health is None or health <= 0:
                continue
            pos = CF.CreatePos(entity_id).GetFootPos()
            if pos is None or any(abs(a - b) > work_range for a, b in zip(pos, centre)):
                continue
            distance_squared = sum((a - b) ** 2 for a, b in zip(pos, centre))
            targets.append((distance_squared, entity_id, pos))

        # Cost grows with Euclidean distance, so an unaffordable nearest
        # target also means no remaining, more distant target can be paid for.
        targets.sort(key=lambda target: target[0])
        for distance_squared, entity_id, pos in targets:
            shock_rf = get_shock_rf(sqrt(distance_squared))
            if self.store_rf < shock_rf:
                break
            if not CF.CreateHurt(entity_id).Hurt(
                SHOCK_DAMAGE, ActorDamageCause.Lightning, None, None, False
            ):
                continue
            self.ReducePower(shock_rf)
            hit_ids.append(entity_id)
            hit_positions.append([float(v) for v in pos])
        self.PowerEnough()
        if hit_ids:
            TeslaPlantAttack(
                self.dim, self.x, self.y, self.z, hit_ids, hit_positions
            ).sendMulti(block_sync.get_players((self.dim, self.x, self.y, self.z)))
            self.CallSync()

    def get_settings_update(self):
        return TeslaPlantSettingsUpdate(
            self.dim, self.x, self.y, self.z, self.work_range,
            self.do_attack_monster, self.do_attack_mob, self.do_attack_player,
        )

    def update_settings(self, do_attack_mob, do_attack_player, do_attack_monster, work_range):
        # type: (bool, bool, bool, int) -> None
        self.bdata[K_SETTING_ATTACK_MOB] = do_attack_mob
        self.bdata[K_SETTING_ATTACK_PLAYER] = do_attack_player
        self.bdata[K_SETTING_ATTACK_MONSTER] = do_attack_monster
        self.bdata[K_SETTING_WORK_RANGE] = work_range
        self._tesla_plant_on_sync()

    @property
    def do_attack_mob(self):
        return self.bdata[K_SETTING_ATTACK_MOB]

    @property
    def do_attack_player(self):
        return self.bdata[K_SETTING_ATTACK_PLAYER]

    @property
    def do_attack_monster(self):
        return self.bdata[K_SETTING_ATTACK_MONSTER]

    @property
    def work_range(self):
        return self.bdata[K_SETTING_WORK_RANGE]


@TeslaPlant.ForOperation(TeslaPlantSettingsUpload)
def on_settings_upload(event, machine):
    # type: (TeslaPlantSettingsUpload, TeslaPlant) -> None
    if any(type(value) is not int for value in (event.dim, event.x, event.y, event.z)):
        return
    if type(event.work_range) is not int or not MIN_WORK_RANGE <= event.work_range <= MAX_WORK_RANGE:
        return
    if any(type(value) is not bool for value in (
        event.do_attack_mob, event.do_attack_player, event.do_attack_monster
    )):
        return
    if not machine.is_base_block or machine.dim != event.dim:
        return
    machine.update_settings(
        event.do_attack_mob, event.do_attack_player, event.do_attack_monster,
        event.work_range,
    )
