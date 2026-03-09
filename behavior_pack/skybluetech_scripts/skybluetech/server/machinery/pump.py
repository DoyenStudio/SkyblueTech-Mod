# coding=utf-8
# lang: py2
from mod.server.blockEntityData import BlockEntityData
from skybluetech_scripts.tooldelta.api.server.block import (
    GetLiquidBlock,
    GetBlockNameAndAux,
    GetBlockStatesFromAuxValue,
    SetBlock,
    SetLiquidBlock,
)
from ...common.define import flags as rf_flags
from ...common.define.id_enum import PUMP as MACHINE_ID, Upgraders
from ...common.define.global_config import BUCKET_VOLUME
from ...common.ui_sync.machinery.pump import PumpUISync
from .basic import (
    FluidContainer,
    GUIControl,
    UpgradeControl,
    RegisterMachine,
)

K_CACHED_VOLUME = "cached_volume"
K_CACHED_FLUID_ID = "cached_fluid_id"


@RegisterMachine
class Pump(FluidContainer, GUIControl, UpgradeControl):
    block_name = MACHINE_ID
    store_rf_max = 8800
    running_power = 20
    input_slots = (0,)
    output_slots = (1,)
    fluid_io_mode = (2, 1, 2, 2, 2, 2)
    max_fluid_volume = 4000
    origin_process_ticks = 5
    upgrade_slot_start = 0
    allow_player_use_bucket_push = False
    allow_upgrader_tags = {
        "skybluetech:upgraders/speed",
        "skybluetech:upgraders/energy",
        "skybluetech:upgraders/expansion",
    }

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        FluidContainer.__init__(self, dim, x, y, z, block_entity_data)
        UpgradeControl.__init__(self, dim, x, y, z, block_entity_data)
        self.sync = PumpUISync.NewServer(self).Activate()
        self.OnSync()
        self.last_over_one_bucket = False

    def OnTicking(self):
        FluidContainer.OnTicking(self)
        if self.ProcessOnce():
            self.work_once()
            self.OnSync()
            self._sending_fluid = True

    def OnSync(self):
        self.sync.fluid_id = self.fluid_id
        self.sync.fluid_volume = self.fluid_volume
        self.sync.max_volume = self.max_fluid_volume
        self.sync.storage_rf = self.store_rf
        self.sync.rf_max = self.store_rf_max
        self.sync.MarkedAsChanged()

    def OnTryActivate(self):
        FluidContainer.OnTryActivate(self)

    def work_once(self):
        if self.cached_volume >= BUCKET_VOLUME * 0.2:
            if self.fluid_id is None:
                self.fluid_id = self.cached_fluid_id
            self.fluid_volume += BUCKET_VOLUME * 0.2
            self.cached_volume -= BUCKET_VOLUME * 0.2
            if self.cached_volume <= 0.0:
                self.cached_fluid_id = None
        else:
            if self.HasUpgrader(Upgraders.GENERIC_EXPANSION_UPGRADER):
                max_dfs_depth = 64
            else:
                max_dfs_depth = 16
            if self.fluid_volume > self.max_fluid_volume - BUCKET_VOLUME:
                return
            res = find_source_block(
                self.dim, self.x, self.y - 1, self.z, self.fluid_id, max_dfs_depth
            )
            if res is None:
                return
            fluid_id, src_pos = res
            src_block_id, _ = GetBlockNameAndAux(self.dim, src_pos)
            if src_block_id != fluid_id:
                SetLiquidBlock(self.dim, src_pos, fluid_id, 1)
            else:
                SetBlock(self.dim, src_pos, fluid_id, 1)
            self.cached_fluid_id = fluid_id
            self.cached_volume += BUCKET_VOLUME * 0.8
            self.fluid_volume += BUCKET_VOLUME * 0.2
            if self.fluid_id is None:
                self.fluid_id = fluid_id

    @property
    def cached_volume(self):
        # type: () -> float
        return self.bdata[K_CACHED_VOLUME] or 0.0

    @cached_volume.setter
    def cached_volume(self, value):
        # type: (float) -> None
        self.bdata[K_CACHED_VOLUME] = value

    @property
    def cached_fluid_id(self):
        # type: () -> str | None
        return self.bdata[K_CACHED_FLUID_ID]

    @cached_fluid_id.setter
    def cached_fluid_id(self, value):
        # type: (str | None) -> None
        self.bdata[K_CACHED_FLUID_ID] = value


def find_source_block(dim, x, y, z, allowed_fluid, max_depth):
    # type: (int, int, int, int, str | None, int) -> tuple[str, tuple[int, int, int]] | None
    block_id, aux = GetLiquidBlock(dim, (x, y, z))
    if block_id is None:
        return None
    if allowed_fluid is not None:
        if block_id != allowed_fluid:
            return None
    fluid_depth = GetBlockStatesFromAuxValue(block_id, aux).get("liquid_depth")
    if fluid_depth is None:
        return None
    elif fluid_depth == 0:
        return block_id, (x, y, z)
    walked = set()
    if fluid_depth >= 8:
        res = _vertical_find_source_block(dim, x, y, z, block_id, walked, 0, max_depth)
    else:
        res = _dfs_find_source_block(
            dim, x, y, z, block_id, walked, fluid_depth, 0, max_depth
        )
    if res is None:
        return None
    else:
        return block_id, res


def _dfs_find_source_block(
    dim,  # type: int
    x,  # type: int
    y,  # type: int
    z,  # type: int
    fluid_id,  # type: str
    walked,  # type: set[tuple[int, int, int]]
    last_fluid_depth,  # type: int
    current_depth,  # type: int
    max_depth,  # type: int
):
    # type: (...) -> tuple[int, int, int] | None
    if current_depth > max_depth:
        return None
    for new_pos in (
        (x - 1, y, z),
        (x + 1, y, z),
        (x, y, z - 1),
        (x, y, z + 1),
    ):
        if new_pos in walked:
            continue
        walked.add(new_pos)
        block_id, aux = GetLiquidBlock(dim, new_pos)
        if block_id is None or block_id != fluid_id:
            continue
        fluid_depth = GetBlockStatesFromAuxValue(block_id, aux).get("liquid_depth")
        if fluid_depth is None:
            continue
        elif fluid_depth == 0:
            return new_pos
        elif fluid_depth >= 8:
            nx, ny, nz = new_pos
            res = _vertical_find_source_block(
                dim,
                nx,
                ny,
                nz,
                fluid_id,
                walked,
                current_depth + 1,
                max_depth,
            )
            if res is not None:
                return res
            else:
                continue
        else:
            nx, ny, nz = new_pos
            if last_fluid_depth < 8 and fluid_depth >= last_fluid_depth:
                continue
            res = _dfs_find_source_block(
                dim,
                nx,
                ny,
                nz,
                fluid_id,
                walked,
                fluid_depth,
                current_depth + 1,
                max_depth,
            )
            if res is not None:
                return res
            else:
                continue
    return None


def _vertical_find_source_block(
    dim,  # type: int
    x,  # type: int
    y,  # type: int
    z,  # type: int
    fluid_id,  # type: str
    walked,  # type: set[tuple[int, int, int]]
    current_depth,  # type: int
    max_depth,  # type: int
):
    current_y = y
    while True:
        current_y += 1
        current_depth += 1
        if current_depth > max_depth:
            return None
        walked.add((x, current_y, z))
        block_id, aux = GetLiquidBlock(dim, (x, current_y, z))
        if block_id is None or block_id != fluid_id:
            return None
        liquid_depth = GetBlockStatesFromAuxValue(block_id, aux).get("liquid_depth")
        if liquid_depth is None:
            continue
        elif liquid_depth == 0:
            return (x, current_y, z)
        elif liquid_depth < 8:
            return _dfs_find_source_block(
                dim,
                x,
                current_y,
                z,
                fluid_id,
                walked,
                liquid_depth,
                current_depth,
                max_depth,
            )
