# coding=utf-8
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID

from ...common.define import flags
from ...common.define.global_config import BUCKET_VOLUME
from ...common.define.id_enum import Machinery, Upgraders
from ...common.machinery_def.pump import (
    K_CACHED_FLUID_ID,
    K_CACHED_VOLUME,
    MAX_FLUID_VOLUME,
    STORE_RF_MAX,
)
from .basic import (
    MultiFluidContainer,
    GUIControl,
    UpgradeControl,
)
from .core import RegisterMachine


@RegisterMachine
class Pump(UpgradeControl, GUIControl, MultiFluidContainer):
    block_name = Machinery.PUMP
    store_rf_max = STORE_RF_MAX
    running_power = 20
    item_input_slots = (0,)
    item_output_slots = (1,)
    fluid_io_mode = (2, 1, 2, 2, 2, 2)
    fluid_slot_max_volumes = {0: MAX_FLUID_VOLUME}
    fluid_input_slots = ()
    fluid_output_slots = (0,)
    migrate_legacy_fluid_data = True
    origin_process_ticks = 5
    upgrade_slot_start = 0
    allow_player_use_bucket_push = False
    allow_upgraders = frozenset({
        Upgraders.BASIC_SPEED_UPGRADER,
        Upgraders.BASIC_ENERGY_UPGRADER,
        Upgraders.GENERIC_EXPANSION_UPGRADER,
    })

    def __init__(self, dim, x, y, z, block_entity_data):
        super(Pump, self).__init__(dim, x, y, z, block_entity_data)
        self.last_over_one_bucket = False
        self.handler.SubscribeOnTicking(self._pump_on_ticking)

    def _pump_on_ticking(self):
        if self.ProcessOnce():
            self.work_once()

    def set_idle_reason(self, reason):
        # type: (int) -> None
        "没能抽取的原因 (0 = 正常抽取): 储罐已满 = FLUID_FULL, 下方没有可抽的流体 = NO_INPUT。"
        for flag in (flags.DEACTIVE_FLAG_FLUID_FULL, flags.DEACTIVE_FLAG_NO_INPUT):
            self.UpdateDeactiveFlag(flag, flag == reason)

    def work_once(self):
        fluid = self.fluids[0]
        if self.cached_volume > 0:
            if self.cached_fluid_id is None:
                self.cached_volume = 0.0
                return
            volume = min(self.cached_volume, BUCKET_VOLUME * 0.2)
            _, remaining = self.OutputFluid(self.cached_fluid_id, volume, 0, True)
            self.cached_volume -= volume - remaining
            self.set_idle_reason(flags.DEACTIVE_FLAG_FLUID_FULL if remaining >= volume else 0)
        else:
            if self.HasUpgrader(Upgraders.GENERIC_EXPANSION_UPGRADER):
                max_dfs_depth = 64
            else:
                max_dfs_depth = 16
            if fluid.volume > fluid.max_volume - BUCKET_VOLUME:
                self.set_idle_reason(flags.DEACTIVE_FLAG_FLUID_FULL)
                return
            res = find_source_block(
                self.dim, self.x, self.y - 1, self.z, fluid.fluid_id, max_dfs_depth
            )
            if res is None:
                self.set_idle_reason(flags.DEACTIVE_FLAG_NO_INPUT)
                return
            fluid_id, src_pos = res
            block_data = CF.CreateBlockInfo(LEVEL_ID).GetBlockNew(src_pos, self.dim)
            src_block_id, _ = (None, 0) if block_data is None else (block_data["name"], block_data["aux"])
            if src_block_id != fluid_id:
                CF.CreateBlockInfo(LEVEL_ID).SetLiquidBlock(
                    src_pos,
                    {"name": fluid_id, "aux": 1},
                    dimensionId=self.dim,
                )
            else:
                CF.CreateBlockInfo(LEVEL_ID).SetBlockNew(
                    src_pos,
                    {"name": fluid_id, "aux": 1},
                    0,
                    dimensionId=self.dim,
                )
            self.cached_fluid_id = fluid_id
            self.cached_volume = BUCKET_VOLUME
            volume = BUCKET_VOLUME * 0.2
            _, remaining = self.OutputFluid(fluid_id, volume, 0, True)
            self.cached_volume -= volume - remaining
            self.set_idle_reason(0)

    @property
    def cached_volume(self):
        # type: () -> float
        return self.bdata[K_CACHED_VOLUME] or 0.0

    @cached_volume.setter
    def cached_volume(self, value):
        # type: (float) -> None
        if value <= 0:
            value = 0.0
            self.cached_fluid_id = None
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
    block_data = CF.CreateBlockInfo(LEVEL_ID).GetLiquidBlock((x, y, z), dim)
    block_id, aux = (None, 0) if block_data is None else (block_data["name"], block_data["aux"])
    if block_id is None:
        return None
    if allowed_fluid is not None:
        if block_id != allowed_fluid:
            return None
    fluid_depth = CF.CreateBlockState(LEVEL_ID).GetBlockStatesFromAuxValue(block_id, aux).get(
        "liquid_depth",
    )
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
        block_data = CF.CreateBlockInfo(LEVEL_ID).GetLiquidBlock(new_pos, dim)
        block_id, aux = (None, 0) if block_data is None else (block_data["name"], block_data["aux"])
        if block_id is None or block_id != fluid_id:
            continue
        fluid_depth = CF.CreateBlockState(LEVEL_ID).GetBlockStatesFromAuxValue(block_id, aux).get(
            "liquid_depth",
        )
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
        block_data = CF.CreateBlockInfo(LEVEL_ID).GetLiquidBlock((x, current_y, z), dim)
        block_id, aux = (None, 0) if block_data is None else (block_data["name"], block_data["aux"])
        if block_id is None or block_id != fluid_id:
            return None
        liquid_depth = CF.CreateBlockState(LEVEL_ID).GetBlockStatesFromAuxValue(block_id, aux).get(
            "liquid_depth",
        )
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
