# coding=utf-8
from weakref import ref
from mod_log import logger
from skybluetech_scripts.tooldelta.api.server import (
    AddBlocksToBlockRemoveListener,
    GetBlockPaletteBetweenPos,
    GetBlockCardinalFacing,
    GetBlockName,
)
from skybluetech_scripts.tooldelta.api.client import (
    GetBlankBlockPalette,
)
from skybluetech_scripts.tooldelta.events.server import (
    BlockRemoveServerEvent,
    EntityPlaceBlockAfterServerEvent,
    ChunkAcquireDiscardedServerEvent,
    ChunkLoadedServerEvent,
)
from skybluetech_scripts.tooldelta.api.common import Delay, ExecLater
from skybluetech_scripts.tooldelta.general import ServerInitCallback
from skybluetech_scripts.tooldelta.extensions.singleblock_model_loader import (
    GeometryModel,
    CreateBlankModel,
)
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ....common.events.misc.multi_block_structure_check import (
    MultiBlockStructureCheckRequest,
    MultiBlockStructureCheckResponse,
)
from ....common.define.flags import (
    DEACTIVE_FLAG_STRUCTURE_BROKEN,
    DEACTIVE_FLAG_STRUCTURE_BLOCK_LACK,
)
from .base_machine import BaseMachine, GUIControl


if 0:
    from typing import TypeVar, Any
    from .base_machine import BaseMachine

    MT = TypeVar("MT", bound=BaseMachine)
    BLOCK_PAT_INDEX = int
    POS_SET = set[tuple[int, int, int]]

DEBUG = False

FLAG_OK = 0
block_removed_listen_pool = set()  # type: set[str]
server_inited = False

ROT_TIMES_MAPPING = {"north": 0, "west": 1, "south": 2, "east": 3}
detect_areas = {}  # type: dict[int, set[DetectArea]]
chunks_to_detect = {}  # type: dict[int, dict[tuple[int, int], list[DetectArea]]]
loaded_chunks = set()  # type: set[tuple[int, int]]


def add_detect_area(dim, area):
    # type: (int, DetectArea) -> None
    detect_areas.setdefault(dim, set()).add(area)


def remove_detect_area(dim, area):
    # type: (int, DetectArea) -> None
    detect_areas[dim].remove(area)
    if not detect_areas[dim]:
        del detect_areas[dim]
    for xz in area.chunks_in_area:
        chunks_to_detect[dim][xz].remove(area)


def rotate_90(x, z, center_x, center_z, y):
    # type: (int, int, int, int, int) -> tuple[int, int, int]
    dx = x - center_x
    dz = z - center_z
    return (center_x + dz, y, center_z - dx)


class DetectArea(object):
    def __init__(self, dim, center_x, center_y, center_z, bound_machine):
        # type: (int, int, int, int, MultiBlockStructure) -> None
        pal = bound_machine._palette
        self.dim = dim
        self.min_y = pal.min_y + center_y
        self.max_y = pal.max_y + center_y
        self.center_x = center_x
        self.center_y = center_y
        self.center_z = center_z
        self._bound_machine = ref(bound_machine)
        palette = bound_machine.structure_palette
        if palette is None:
            raise ValueError("StructureBlockPalette: palette is None")
        self.palette = palette
        self.functional_block_poses = {}  # type: dict[str, list[tuple[int, int, int]]]
        core_block_facing = GetBlockCardinalFacing(
            self.dim, (self.center_x, self.center_y, self.center_z)
        )
        self.min_x, self.min_z, self.max_x, self.max_z = {
            "north": (
                center_x + pal.min_x,
                center_z + pal.min_z,
                center_x + pal.max_x,
                center_z + pal.max_z,
            ),
            "south": (
                center_x - pal.max_x,
                center_z - pal.max_z,
                center_x - pal.min_x,
                center_z - pal.min_z,
            ),
            "east": (
                center_x - pal.max_z,
                center_z + pal.min_x,
                center_x - pal.min_z,
                center_z + pal.max_x,
            ),
            "west": (
                center_x + pal.min_z,
                center_z - pal.max_x,
                center_x + pal.max_z,
                center_z - pal.min_x,
            ),
        }[core_block_facing]
        self.chunks_in_area = get_chunks_in_range(
            self.min_x, self.min_z, self.max_x, self.max_z
        )
        self.chunks_not_loaded = get_not_loaded_chunk_poses_in_range(
            self.min_x, self.min_z, self.max_x, self.max_z
        )
        for chunk_xz in self.chunks_in_area:
            chunks_to_detect.setdefault(self.dim, {}).setdefault(chunk_xz, []).append(
                self
            )

    def is_inside(self, x, y, z):
        return (
            x >= self.min_x
            and x <= self.max_x
            and y >= self.min_y
            and y <= self.max_y
            and z >= self.min_z
            and z <= self.max_z
        )

    def get_expected_structure(self):
        spalette = self.palette
        core_block_facing = GetBlockCardinalFacing(
            self.dim, (self.center_x, self.center_y, self.center_z)
        )
        rotation_times = ROT_TIMES_MAPPING[core_block_facing]
        for _i in range(rotation_times):
            spalette = spalette.rotate()
        return (
            {
                k: [
                    (x + self.center_x, y + self.center_y, z + self.center_z)
                    for x, y, z in v
                ]
                for k, v in spalette.posblock_data.items()
            },
            self.palette.palette_data,
        )

    def flush_status(self):
        flag = self.detect()
        if flag == FLAG_OK:
            if DEBUG:
                logger.info("Detect OK")
            self.bound.UnsetStructureDestroyed()
        else:
            if DEBUG:
                logger.info("Detect failed, flag is %d" % flag)
            self.bound.SetStructureDestroyed(flag)

    def detect(self):
        if self.chunks_not_loaded:
            return DEACTIVE_FLAG_STRUCTURE_BROKEN
        else:
            return self._detect_structure()

    def add_loaded_chunk(self, chunk_xz):
        # type: (tuple[int, int]) -> None
        self.chunks_not_loaded.discard(chunk_xz)
        self.flush_status()

    def discard_loaded_chunk(self, chunk_xz):
        # type: (tuple[int, int]) -> None
        self.chunks_not_loaded.add(chunk_xz)
        self.flush_status()

    def _update_functional_blocks(self, palette, co_x, co_y, co_z):
        # type: (Any, int, int, int) -> None
        self.functional_block_poses = {
            block_id: [
                (
                    x - co_x + self.center_x,
                    y - co_y + self.center_y,
                    z - co_z + self.center_z,
                )
                for x, y, z in palette.GetLocalPosListOfBlocks(block_id)
            ]
            for block_id in self.bound.functional_block_ids
        }

    def get_box(self):
        return (
            (self.min_x, self.min_y, self.min_z),
            (self.max_x, self.max_y, self.max_z),
        )

    def _detect_structure(self):
        spalette = self.palette
        current_palette = GetBlockPaletteBetweenPos(
            self.dim,
            (self.min_x, self.min_y, self.min_z),
            (self.max_x, self.max_y, self.max_z),
            eliminateAir=False,
        )
        if current_palette is None:
            logger.error("[Error] Palette is None")
            return DEACTIVE_FLAG_STRUCTURE_BROKEN
        co_x = self.center_x - self.min_x
        co_y = self.center_y - self.min_y
        co_z = self.center_z - self.min_z
        core_block_facing = GetBlockCardinalFacing(
            self.dim, (self.center_x, self.center_y, self.center_z)
        )
        rotation_times = ROT_TIMES_MAPPING[core_block_facing]
        for _i in range(rotation_times):
            spalette = spalette.rotate()
        if spalette.compare(
            current_palette,
            self.dim,
            co_x,
            co_y,
            co_z,
            self.center_x,  # debug param
            self.center_y,  # debug param
            self.center_z,  # debug param
        ):
            lacked_blocks = spalette.get_lacked_blocks(current_palette)
            if lacked_blocks is None:
                self._update_functional_blocks(current_palette, co_x, co_y, co_z)
                return FLAG_OK
            else:
                self.bound._lacked_blocks = lacked_blocks
                return DEACTIVE_FLAG_STRUCTURE_BLOCK_LACK
        return DEACTIVE_FLAG_STRUCTURE_BROKEN

    @property
    def bound(self):
        bound_machine = self._bound_machine()
        if bound_machine is None:
            raise ValueError("bound_machine is None")
        if bound_machine.area != self:
            raise ValueError("bound_machine.area != self")
        return bound_machine

    @property
    def has_bound(self):
        return self._bound_machine() is not None

    @property
    def inited(self):
        return not self.chunks_not_loaded

    def __hash__(self):
        return hash((
            self.min_x,
            self.min_y,
            self.min_z,
            self.max_x,
            self.max_y,
            self.max_z,
        ))


class StructureBlockPalette(object):
    """
    多方块检测调色板, 用于表示多方块结构的内容。
    核心方块总是在内部坐标 `(0, 0, 0)` 处。

    注意: 核心只能朝北面放置, 也就是说朝向玩家的那面为南面。
    """

    def __init__(
        self,
        posblock_data,  # type: dict[int, set[tuple[int, int, int]]]
        palette_data,  # type: dict[int, str | list[str]]
        min_x,  # type: int
        min_y,  # type: int
        min_z,  # type: int
        max_x,  # type: int
        max_y,  # type: int
        max_z,  # type: int
        require_blocks_count,  # type: dict[str, int]
        _rotation=0,
    ):
        # type: (...) -> None
        # 原点坐标为 (0, 0, 0)
        self.posblock_data = posblock_data
        self.palette_data = palette_data
        self.min_x = min_x
        self.min_y = min_y
        self.min_z = min_z
        self.max_x = max_x
        self.max_y = max_y
        self.max_z = max_z
        self.require_blocks_count = require_blocks_count
        self._rotation = _rotation
        # self.all_poses = set(j for i in posblock_data.values() for j in i)
        if not server_inited:
            for block_id in palette_data.values():
                if isinstance(block_id, str):
                    block_removed_listen_pool.add(block_id)
                else:
                    block_removed_listen_pool.update(block_id)

    def compare(self, block_palette, dim, co_x, co_y, co_z, cx, cy, cz):
        # type: (Any, int, int, int, int, int, int, int) -> bool
        """
        比较方块调色板内容是否与此调色板匹配。

        Args:
            block_palette (BlockPaletteComponent): 调色板
            co_x (int): 调色板中心偏移x
            co_z (int): 调色板中心偏移z
        """
        for index, block_ids in self.palette_data.items():
            if isinstance(block_ids, str):
                block_ids = [block_ids]
            actua_pos_set = set(
                (x - co_x, y - co_y, z - co_z)
                for block_id in block_ids
                for x, y, z in block_palette.GetLocalPosListOfBlocks(block_id)
            )
            expected_pos_set = self.posblock_data[index]
            if len(actua_pos_set & expected_pos_set) < len(expected_pos_set):
                if DEBUG:
                    debug_show_diff(
                        dim, cx, cy, cz, expected_pos_set, actua_pos_set, block_ids
                    )
                return False
        return True

    def get_lacked_blocks(self, block_palette):
        # type: (Any) -> dict[str, int] | None
        for block_id, count in self.require_blocks_count.items():
            if block_palette.GetBlockCountInBlockPalette(block_id) < count:
                return {
                    block_id: count
                    for block_id, count in self.require_blocks_count.items()
                    if block_palette.GetBlockCountInBlockPalette(block_id) < count
                }
        return None

    def rotate(self):
        # type: () -> StructureBlockPalette
        x1, _, z1 = rotate_90(self.min_x, self.min_z, 0, 0, self.min_y)
        x2, _, z2 = rotate_90(self.max_x, self.max_z, 0, 0, self.max_y)
        new_min_x = min(x1, x2)
        new_max_x = max(x1, x2)
        new_min_z = min(z1, z2)
        new_max_z = max(z1, z2)
        newPosBlockDat = {
            idx: set(rotate_90(x, z, 0, 0, y) for x, y, z in poses)
            for idx, poses in self.posblock_data.items()
        }
        return StructureBlockPalette(
            newPosBlockDat,
            self.palette_data,
            new_min_x,
            self.min_y,
            new_min_z,
            new_max_x,
            self.max_y,
            new_max_z,
            self.require_blocks_count,
            _rotation=self._rotation + 90,
        )


class MultiBlockStructure(BaseMachine):
    """
    多方块机器结构的基类。

    派生自: `BaseMachine`

    需要调用 `__init__`

    覆写:
        `OnLoad`
        `OnUnload`

    Class Attributes:
        structure_palette (StructureBlockPalette | None): 检测多方块结构完整性的结构调色板
        functional_block_ids (set[str]): 多方块结构中功能性方块的列表。GetMachine() 获取的机器方块 id 都需要被包含在其中。
    """

    structure_palette = None  # type: StructureBlockPalette | None
    "用于进行多方块完整性检测的多方块结构调色板。"
    functional_block_ids = set()  # type: set[str]
    "多方块结构中功能性方块的列表。"

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        if self.structure_palette is None:
            raise ValueError("StructureBlockPalette: structure_palette is None")
        self._last_destroy_flag = DEACTIVE_FLAG_STRUCTURE_BROKEN
        self._lacked_blocks = {}  # type: dict[str, int]
        self._palette = self.structure_palette
        self.dim = dim
        self.x = x
        self.y = y
        self.z = z
        self.area = DetectArea(self.dim, self.x, self.y, self.z, self)
        add_detect_area(self.dim, self.area)

    def OnStructureChanged(self, structure_finished):
        # type: (bool) -> None
        "覆写方法用于结构变更的回调。"

    def OnUnload(self):

        remove_detect_area(self.dim, self.area)

    def SetStructureDestroyed(self, flag):
        # type: (int) -> None
        self._last_destroy_flag = flag
        self.area.functional_block_poses = {}
        self.SetDeactiveFlag(flag)
        self.OnStructureChanged(False)
        if isinstance(self, GUIControl):
            self.CallSync()

    def UnsetStructureDestroyed(self):
        if self._last_destroy_flag != FLAG_OK:
            self.UnsetDeactiveFlag(self._last_destroy_flag)
            self._last_destroy_flag = FLAG_OK
            self._lacked_blocks = {}
            self.OnStructureChanged(True)
            if isinstance(self, GUIControl):
                self.CallSync()

    def GetStructureDestroyFlag(self):
        return self._last_destroy_flag

    def GetStructureLackedBlocks(self):
        return self._lacked_blocks

    def GetFunctionalBlockPoses(self):
        "返回功能性方块对于多方块结构核心位置的相对坐标。"
        return self.area.functional_block_poses

    def StructureFinished(self):
        return self._last_destroy_flag == 0

    # StructureUtils

    def GetExpectedStructure(self):
        return self.area.get_expected_structure()

    def GetAllMachines(self, cls, block_id=None):
        # type: (type[MT], str | None) -> list[MT]
        from ..pool import GetMachineStrict

        block_id = block_id or cls.block_name
        poses = self.GetFunctionalBlockPoses().get(block_id, [])
        machines = []
        for pos in poses:
            m = GetMachineStrict(self.dim, *pos)
            if isinstance(m, cls):
                machines.append(m)
        return machines

    def GetMachine(self, cls, block_id, index=0):
        # type: (type[MT], str | None, int) -> MT
        """
        获取多方块结构中某一类型的机器(多用于多方块结构接口的获取)。
        其 ID 需要被包含在类属性 `functional_block_ids` 中。

        Args:
            cls (type[BaseMachine]): 机器类
            block_id (str, optional): 机器方块 ID
            index (int, optional): 索引值, 如果有多个匹配的机器则使用索引值。

        Raises:
            ValueError: 找不到对应机器

        Returns:
            BaseMachine: 所求机器类
        """
        block_id = block_id or cls.block_name
        pos = self.GetFunctionalBlockPoses().get(block_id)
        if not pos:
            raise ValueError("Cannot find block: %s" % block_id)
        from ..pool import GetMachineStrict

        x, y, z = pos[index]
        machine = GetMachineStrict(self.dim, x, y, z)
        if not isinstance(machine, cls):
            raise ValueError(
                "({}, {}, {}): {} is not a {}".format(
                    x, y, z, type(machine).__name__, cls.__name__
                )
            )
        return machine

    def TryGetMachine(self, cls, block_id=None, index=0):
        # type: (type[MT], str | None, int) -> MT | None
        """GetMachine 的可空返回版本, 获取不到对应机器则返回 None"""
        block_id = block_id or cls.block_name
        pos = self.GetFunctionalBlockPoses().get(block_id)
        if not pos:
            return None
        from ..pool import GetMachineStrict

        x, y, z = pos[index]
        machine = GetMachineStrict(self.dim, x, y, z)
        if not isinstance(machine, cls):
            raise ValueError(
                "({}, {}, {}): {} is not a {}".format(
                    x, y, z, type(machine).__name__, cls.__name__
                )
            )
        return machine


def GenerateSimpleStructureTemplate(
    key,  # type: dict[str, str] | dict[str, str | list[str]]
    pattern,  # type: dict[int, list[str]]
    center_block_sign="#",  # type: str
    require_blocks_count=None,  # type: dict[str, int] | None
):
    # type: (...) -> StructureBlockPalette
    """
    key: 单字母键 -> 方块 ID
    """
    orig_posblock_data = {}  # type: dict[BLOCK_PAT_INDEX, POS_SET]
    palette_data = {}  # type: dict[int, str | list[str]]
    pat2idx = {}  # type: dict[str, int]
    offset_x = None  # type: int | None
    offset_y = None  # type: int | None
    offset_z = None  # type: int | None
    min_x = 999
    min_y = 999
    min_z = 999
    max_x = -999
    max_y = -999
    max_z = -999

    def get_index_by_pattern(pattern):
        # type: (str) -> BLOCK_PAT_INDEX
        if pattern not in pat2idx:
            idx = pat2idx[pattern] = len(pat2idx)
            palette_data[idx] = key[pattern]
        return pat2idx[pattern]

    for layer, platform in pattern.items():
        if layer < min_y:
            min_y = layer
        elif layer > max_y:
            max_y = layer
        for z, row_data in enumerate(platform):
            if z < min_z:
                min_z = z
            elif z > max_z:
                max_z = z
            for x, pat in enumerate(row_data):
                if pat == " ":
                    continue
                if x < min_x:
                    min_x = x
                elif x > max_x:
                    max_x = x
                if pat == center_block_sign:
                    offset_x = x
                    offset_y = layer
                    offset_z = z
                    continue
                idx = get_index_by_pattern(pat)
                orig_posblock_data.setdefault(idx, set()).add((x, layer, z))

    if offset_x is None or offset_y is None or offset_z is None:
        raise ValueError("Invalid pattern")

    posblock_data = {
        k: {(x - offset_x, y - offset_y, z - offset_z) for x, y, z in v}
        for k, v in orig_posblock_data.items()
    }
    return StructureBlockPalette(
        posblock_data,
        palette_data,
        min_x - offset_x,
        min_y - offset_y,
        min_z - offset_z,
        max_x - offset_x,
        max_y - offset_y,
        max_z - offset_z,
        require_blocks_count or {},
    )


def get_chunks_in_range(startx, startz, endx, endz):
    # type: (int, int, int, int) -> set[tuple[int, int]]
    startx, endx = sorted([startx, endx])
    startz, endz = sorted([startz, endz])
    return {
        (x, z)
        for x in range(startx // 16, endx // 16 + 1)
        for z in range(startz // 16, endz // 16 + 1)
    }


def get_not_loaded_chunk_poses_in_range(startx, startz, endx, endz):
    # type: (int, int, int, int) -> set[tuple[int, int]]
    res = set()  # type: set[tuple[int, int]]
    startx, endx = sorted([startx, endx])
    startz, endz = sorted([startz, endz])
    for x in range(startx // 16, endx // 16 + 1):
        for z in range(startz // 16, endz // 16 + 1):
            p = (x, z)
            if p in loaded_chunks:
                continue
            res.add(p)
    return res


@ServerInitCallback()
def onServerInit():
    global server_inited
    AddBlocksToBlockRemoveListener(block_removed_listen_pool)
    server_inited = True


@EntityPlaceBlockAfterServerEvent.Listen(0)
def onEntityPlaceStruBlock(event):
    # type: (EntityPlaceBlockAfterServerEvent) -> None
    x = event.x
    y = event.y
    z = event.z
    for area in detect_areas.get(event.dimensionId, set()):
        if not area.has_bound:
            logger.error(
                "SkyblueTech: DetectArea not bound machine at {}".format(area.get_box())
            )
            continue
        if area.inited and area.bound._last_destroy_flag == FLAG_OK:
            continue
        if area.is_inside(x, y, z):
            area.flush_status()


@BlockRemoveServerEvent.Listen(1)
@Delay(0)  # 此时原方块仍然是原方块, 不是空气
def onStruBlockRemoved(event):
    # type: (BlockRemoveServerEvent) -> None
    x = event.x
    y = event.y
    z = event.z
    for area in detect_areas.get(event.dimension, set()):
        if not area.has_bound:
            logger.error(
                "SkyblueTech: DetectArea not bound machine at {}".format(area.get_box())
            )
            continue
        if (
            area.inited
            and area.bound._last_destroy_flag == DEACTIVE_FLAG_STRUCTURE_BROKEN
        ):
            continue
        if area.is_inside(x, y, z):
            if x == area.center_x and y == area.center_y and z == area.center_z:
                return
            ExecLater(0, area.flush_status)


@ChunkLoadedServerEvent.Listen(-1001)
def onChunkLoaded(event):
    # type: (ChunkLoadedServerEvent) -> None
    pos = (event.chunkPosX, event.chunkPosZ)
    loaded_chunks.add(pos)
    areas = chunks_to_detect.get(event.dimension, {}).get(pos)
    if areas is None:
        return
    for area in areas:
        area.add_loaded_chunk(pos)


@ChunkAcquireDiscardedServerEvent.Listen(1001)
def onChunkDiscarded(event):
    # type: (ChunkAcquireDiscardedServerEvent) -> None
    pos = (event.chunkPosX, event.chunkPosZ)
    loaded_chunks.remove(pos)
    areas = chunks_to_detect.get(event.dimension, {}).get(pos)
    if areas is None:
        return
    for area in areas:
        area.discard_loaded_chunk(pos)


@MultiBlockStructureCheckRequest.Listen()
def onCheckRequest(event):
    # type: (MultiBlockStructureCheckRequest) -> None
    from ..utils.action_commit import SafeGetMachine

    m = SafeGetMachine(event.x, event.y, event.z, event.player_id)
    if not isinstance(m, MultiBlockStructure):
        return
    posblock_data, palette = m.GetExpectedStructure()
    MultiBlockStructureCheckResponse(
        event.x, event.y, event.z, palette, posblock_data
    ).send(event.player_id)


# CLIENT PART

multi_block_model_displaying = False


@MultiBlockStructureCheckResponse.Listen()
def onRecvResponse(event):
    # type: (MultiBlockStructureCheckResponse) -> None
    global multi_block_model_displaying
    if multi_block_model_displaying:
        return
    posblock_data = event.pos_block_data
    palette = event.palette
    min_x = 1 << 31
    max_x = -1 << 31
    min_y = 1 << 31
    max_y = -1 << 31
    min_z = 1 << 31
    max_z = -1 << 31
    for x, y, z in ((_x, _y, _z) for v in posblock_data.values() for _x, _y, _z in v):
        if x < min_x:
            min_x = x
        if x > max_x:
            max_x = x
        if y < min_y:
            min_y = y
        if y > max_y:
            max_y = y
        if z < min_z:
            min_z = z
        if z > max_z:
            max_z = z
    size_x = max_x - min_x + 1
    size_y = max_y - min_y + 1
    size_z = max_z - min_z + 1
    volume = size_x * size_y * size_z
    if volume > 48 * 48 * 48:
        logger.error(
            "[Error] display multi block structure model too large: %d" % volume
        )
        return
    palette_display = {
        k: (v if isinstance(v, str) else v[0]) for k, v in palette.items()
    }
    pal_dict = {}  # type: dict[tuple[str, int], list[int]]
    for pal_index, posblocks in posblock_data.items():
        for x, y, z in posblocks:
            pal_dict.setdefault((palette_display[pal_index], 0), []).append(
                (y - min_y) * size_x * size_z + (x - min_x) * size_z + (z - min_z)
            )
    pal = GetBlankBlockPalette()
    pal.DeserializeBlockPalette({
        "extra": {},
        "void": False,
        "actor": {},
        "volume": (size_x, size_y, size_z),
        "common": pal_dict,
        "eliminateAir": True,
    })
    multi_block_model_displaying = True
    geo_model = CreateBlankModel((min_x, min_y, min_z))
    geo_model.SetBlockPaletteModel(pal, "skybluetech_multi_block_model_display")
    remove_get_model_later(geo_model)


@Delay(4)
def remove_get_model_later(geo_model):
    # type: (GeometryModel) -> None
    global multi_block_model_displaying
    geo_model.Destroy()
    multi_block_model_displaying = False


def debug_show_diff(
    dim,  # type: int
    x,  # type: int
    y,  # type: int
    z,  # type: int
    expected,  # type: set[tuple[int, int, int]]
    actual,  # type: set[tuple[int, int, int]]
    expected_block_ids,
):
    print("====== Structure not equal ======")
    print("Expected blocks: {}".format(expected_block_ids))
    print("No equal poses ({} < {}) :".format(len(actual & expected), len(expected)))
    for _x, _y, _z in expected.difference(actual):
        print(
            " ({} {} {}) : {}".format(
                x + _x, y + _y, z + _z, GetBlockName(dim, (x + _x, y + _y, z + _z))
            )
        )
    print("====== Structure debug end ======")
