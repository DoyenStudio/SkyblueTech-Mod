# coding=utf-8
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
from ...common.define.global_config import BUCKET_VOLUME
from ...common.define.id_enum import Machinery
from ...common.events.machinery.effluent_outfall import EffluentOutfallDischarge
from ...common.machinery_def.effluent_outfall import EffluentOutfallRecipe, classify_biome, find_recipe
from .basic import MultiFluidContainer
from .core import RegisterMachine
from .utils.transmitter_conn import TransmitterConn


TCON = TransmitterConn(fluid_pipe=True)
K_BIOME = "st:outfall_biome_group"
BUFFER = 0
UNLIMITED_INLETS = (1, 2)
MIN_WATER_BLOCKS = 27
WATER_RECHECK_TICKS = 20
WATER_BLOCKS = ("minecraft:water", "minecraft:flowing_water")
AIR = {"name": "minecraft:air", "aux": 0}


@RegisterMachine
class EffluentOutfall(MultiFluidContainer):
    block_name = Machinery.EFFLUENT_OUTFALL
    is_non_energy_machine = True
    store_rf_max = 0
    energy_io_mode = (2,) * 6
    fluid_io_mode = (0,) * 6
    fluid_input_slots = (BUFFER,) + UNLIMITED_INLETS
    fluid_output_slots = ()
    # 限速槽能容纳最快配方的一秒用量。两个水槽允许同一秒内分别接收两种水。
    # 使用有限容量，避免触发框架的创造供液槽语义。
    fluid_slot_max_volumes = {BUFFER: 2 * BUCKET_VOLUME, 1: 2147483647, 2: 2147483647}
    allow_player_use_bucket_pull = False

    def __init__(self, dim, x, y, z, block_entity_data):
        super(EffluentOutfall, self).__init__(dim, x, y, z, block_entity_data)
        self._biome = self.bdata[K_BIOME]
        self._submerged = None
        self._water_recheck_ticks = 1
        self._settlement_ticks = 0
        self.handler.SubscribeOnPlaced(self._on_placed)
        self.handler.SubscribeOnNeighborChanged(self._on_neighbor_changed)
        self.handler.SubscribeOnTicking(self._on_tick)

    def _on_placed(self, _):
        self._refresh_water()
        TCON.block_placed(self)

    def _on_neighbor_changed(self, event):
        self._refresh_water()
        TCON.neighbor_block_changed(self, event)

    def _refresh_water(self):
        self._submerged = self._has_enough_water()
        # 非相邻水格的变化也可能改变结果，达标后仍需定期复查。
        self._water_recheck_ticks = 1 if self._submerged is False else WATER_RECHECK_TICKS
        if self._submerged and self._biome is None:
            name = CF.CreateBiome(LEVEL_ID).GetBiomeName(self.xyz, self.dim)
            if name:
                self._biome = self.bdata[K_BIOME] = classify_biome(name)

    def _has_enough_water(self):
        chunks = CF.CreateChunkSource(LEVEL_ID)
        if not chunks.CheckChunkState(self.dim, self.xyz):
            return None
        block_info = CF.CreateBlockInfo(LEVEL_ID)
        center = block_info.GetLiquidBlock(self.xyz, self.dim)
        if not center or center["name"] not in WATER_BLOCKS:
            return False
        cx_self, cz_self = self.x // 16, self.z // 16
        for cx in range((self.x - 1) // 16, (self.x + 1) // 16 + 1):
            for cz in range((self.z - 1) // 16, (self.z + 1) // 16 + 1):
                if (cx, cz) != (cx_self, cz_self) and not chunks.CheckChunkState(
                    self.dim, (cx * 16, self.y, cz * 16)
                ):
                    return None
        count = 1
        for x in range(self.x - 1, self.x + 2):
            for z in range(self.z - 1, self.z + 2):
                for y in range(self.y - 2, self.y + 3):
                    pos = (x, y, z)
                    if pos == self.xyz:
                        continue
                    liquid = block_info.GetLiquidBlock(pos, self.dim)
                    if liquid and liquid["name"] in WATER_BLOCKS:
                        count += 1
                        if count >= MIN_WATER_BLOCKS:
                            return True
        return False

    def _check_and_break(self):
        self._refresh_water()
        if self._submerged is not False:
            return
        self._water_recheck_ticks = WATER_RECHECK_TICKS
        info = CF.CreateBlockInfo(LEVEL_ID)
        block = info.GetBlockNew(self.xyz, self.dim)
        if block and block["name"] == self.block_name:
            # 原生销毁会生成机体掉落，同时保留方块原先含有的流体。
            liquid = info.GetLiquidBlock(self.xyz, self.dim)
            info.SetBlockNew(self.xyz, liquid or AIR, 1, self.dim, True)

    def IsValidFluidInput(self, slot, fluid_id):
        if not self._submerged:
            return False
        recipe = find_recipe(fluid_id, self._biome)
        if recipe is None:
            return False
        if recipe.volume_per_second is None:
            return slot in UNLIMITED_INLETS
        return slot == BUFFER

    def _on_tick(self):
        self._water_recheck_ticks -= 1
        if not self._water_recheck_ticks:
            self._check_and_break()
        self._settlement_ticks += 1
        if self._settlement_ticks < EffluentOutfallRecipe.SETTLEMENT_TICKS:
            return
        self._settlement_ticks = 0
        if not self._submerged:
            return
        for slot in self.fluid_input_slots:
            tank = self.fluids[slot]
            if tank.volume <= 0:
                continue
            fluid_id = tank.fluid_id
            recipe = find_recipe(fluid_id, self._biome)
            if recipe is None:
                continue
            volume = tank.volume
            if recipe.volume_per_second is not None:
                volume = min(volume, recipe.volume_per_second)
            tank.volume -= volume
            self._on_reduced_fluid(slot, fluid_id, volume, True)
            EffluentOutfallDischarge(self.dim, self.xyz, fluid_id).sendAll()
