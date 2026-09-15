# coding=utf-8
from weakref import ref

from mod_log import logger

from skybluetech_scripts.skybluetech.common.define.flags import (
    DEACTIVE_FLAG_STRUCTURE_BLOCK_LACK,
    DEACTIVE_FLAG_STRUCTURE_BROKEN,
)
from skybluetech_scripts.skybluetech.common.events.misc.multi_block_structure_check import (
    MultiBlockStructureCheckRequest,
    MultiBlockStructureCheckResponse,
)
from skybluetech_scripts.skybluetech.common.machinery_def.basic.multi_block_structure import (
    K_DESTROY_FLAG,
    K_STRUCTURE_LACKED_BLOCK_POSES,
    K_STRUCTURE_LACKED_BLOCKS,
)
from skybluetech_scripts.skybluetech.common.utils.structure_palette import (
    AIR_BLOCK_ID,
    StructureBlockPalette,
)
from skybluetech_scripts.tooldelta.api.client import (
    GetBlankBlockPalette,
)
from skybluetech_scripts.tooldelta.api.common import Delay, ExecLater
from skybluetech_scripts.tooldelta.api.server import (
    AddBlocksToBlockRemoveListener,
    GetBlockCardinalFacing,
    GetBlockName,
    GetBlockPaletteBetweenPos,
)
from skybluetech_scripts.tooldelta.events.server import (
    BlockRemoveServerEvent,
    ChunkAcquireDiscardedServerEvent,
    ChunkLoadedServerEvent,
    EntityPlaceBlockAfterServerEvent,
)
from skybluetech_scripts.tooldelta.extensions.singleblock_model_loader import (
    CreateBlankModel,
    GeometryModel,
)
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from skybluetech_scripts.tooldelta.general import (
    ServerInitCallback,
    ServerUninitCallback,
)

from .base_machine import BaseMachine, GUIControl

if 0>1:
    import typing
    from .base_machine import BaseMachine

    MT = typing.TypeVar("MT", bound=BaseMachine)
    BLOCK_PAT_INDEX = int
    POS_SET = typing.Set[typing.Tuple[int, int, int]]

DEBUG = False

FLAG_OK = 0
MAX_STRUCTURE_MISMATCH_POSES = 5
"最多写入方块实体数据的结构不匹配位置数量, 避免 UI 溢出."
STRUCTURE_DEACTIVE_FLAGS = (
    DEACTIVE_FLAG_STRUCTURE_BROKEN | DEACTIVE_FLAG_STRUCTURE_BLOCK_LACK
)
block_removed_listen_pool = set()  # type: set[str]
server_inited = False

ROT_TIMES_MAPPING = {"north": 0, "west": 1, "south": 2, "east": 3}
detect_areas = {}  # type: dict[int, set[DetectArea]]
chunks_to_detect = {}  # type: dict[int, dict[tuple[int, int], list[DetectArea]]]
loaded_chunks = set()  # type: set[tuple[int, int, int]]
"已加载的区块, 按 (维度, 区块x, 区块z) 记录: 不同维度的同坐标区块互不相干。"


def add_detect_area(dim, area):
    # type: (int, DetectArea) -> None
    detect_areas.setdefault(dim, set()).add(area)


def remove_detect_area(dim, area):
    # type: (int, DetectArea) -> None
    "注销检测区域; 重复注销不会报错, 顺手清掉区块索引里留下的空容器。"
    areas = detect_areas.get(dim)
    if areas is None or area not in areas:
        return
    areas.discard(area)
    if not areas:
        del detect_areas[dim]
    chunk_map = chunks_to_detect.get(dim)
    if chunk_map is None:
        return
    for xz in area.chunks_in_area:
        holders = chunk_map.get(xz)
        if not holders:
            continue
        holders[:] = [other for other in holders if other is not area]
        if not holders:
            del chunk_map[xz]
    if not chunk_map:
        del chunks_to_detect[dim]


def drop_orphan_detect_area(area):
    # type: (DetectArea) -> None
    "机器已经卸载, 但检测区域还挂在表里(漏调 `OnUnload` 时), 这里兜底回收。"
    logger.error(
        "SkyblueTech: drop DetectArea of unloaded machine at %s" % (area.get_box(),)
    )
    remove_detect_area(area.dim, area)


dirty_detect_areas = {}  # type: dict[DetectArea, None]
"本 tick 内结构发生变化, 需要在下一 tick 重新检测的检测区域。"
flush_scheduled = False
"是否已经排好一次刷新, 避免同一 tick 内重复排队。"


def mark_detect_area_dirty(area):
    # type: (DetectArea) -> None
    """
    标记检测区域需要在下一 tick 重新检测。

    同一 tick 内的多次方块变化(比如爆炸一次炸掉半个结构)会被合并成一次全量扫描。
    """
    global flush_scheduled
    dirty_detect_areas[area] = None
    if not flush_scheduled:
        flush_scheduled = True
        ExecLater(0, flush_dirty_detect_areas)


def flush_dirty_detect_areas():
    # type: () -> None
    "重新检测所有被标记的检测区域; 机器已经卸载的区域直接跳过。"
    global flush_scheduled
    flush_scheduled = False
    dirty_areas = list(dirty_detect_areas)
    dirty_detect_areas.clear()
    for area in dirty_areas:
        if area.has_bound:
            area.flush_status()


class DetectArea(object):
    def __init__(self, dim, center_x, center_y, center_z, bound_machine):
        # type: (int, int, int, int, MultiBlockStructure) -> None
        pal = bound_machine.structure_palette
        if pal is None:
            raise ValueError("StructureBlockPalette: palette is None")
        self.dim = dim
        self.min_y = pal.min_y + center_y
        self.max_y = pal.max_y + center_y
        self.center_x = center_x
        self.center_y = center_y
        self.center_z = center_z
        self._bound_machine = ref(bound_machine)
        self.palette = pal
        self.functional_block_poses = {}  # type: dict[str, list[tuple[int, int, int]]]
        # 朝向只在初始化时取一次: 下面的包围盒和 `_detect_structure()` 里的旋转都依赖它,
        # 两处用同一个值才能保证始终互相自洽
        self.core_block_facing = GetBlockCardinalFacing(
            self.dim, (self.center_x, self.center_y, self.center_z)
        )
        self.rotation_times = ROT_TIMES_MAPPING[self.core_block_facing]
        self._rotated_palette = None  # type: StructureBlockPalette | None
        self._air_poses_in_world = None  # type: set[tuple[int, int, int]] | None
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
        }[self.core_block_facing]
        self.chunks_in_area = get_chunks_in_range(
            self.min_x, self.min_z, self.max_x, self.max_z
        )
        self.chunks_not_loaded = get_not_loaded_chunk_poses_in_range(
            self.dim, self.min_x, self.min_z, self.max_x, self.max_z
        )
        for chunk_xz in self.chunks_in_area:
            chunks_to_detect.setdefault(self.dim, {}).setdefault(chunk_xz, []).append(
                self
            )
        for block_id in pal.palette_data.values():
            if isinstance(block_id, str):
                block_removed_listen_pool.add(block_id)
            else:
                block_removed_listen_pool.update(block_id)
        if server_inited:
            AddBlocksToBlockRemoveListener(block_removed_listen_pool)
        if not self.chunks_not_loaded:
            mark_detect_area_dirty(self)

    def is_inside(self, x, y, z):
        return (
            x >= self.min_x
            and x <= self.max_x
            and y >= self.min_y
            and y <= self.max_y
            and z >= self.min_z
            and z <= self.max_z
        )

    @property
    def rotated_palette(self):
        # type: () -> StructureBlockPalette
        "按核心朝向旋转后的结构调色板, 只在首次访问时旋转一次。"
        if self._rotated_palette is None:
            spalette = self.palette
            for _i in range(self.rotation_times):
                spalette = spalette.rotate()
            self._rotated_palette = spalette
        return self._rotated_palette

    @property
    def air_poses_in_world(self):
        # type: () -> set[tuple[int, int, int]]
        """
        图案里标成"必须为空"的位置的世界坐标, 只在首次访问时算一次。
        """
        if self._air_poses_in_world is None:
            self._air_poses_in_world = {
                (self.center_x + x, self.center_y + y, self.center_z + z)
                for x, y, z in self.rotated_palette.air_poses
            }
        return self._air_poses_in_world

    def get_expected_structure(self):
        spalette = self.rotated_palette
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
            self.bound.lacked_block_poses = []
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
        # type: (typing.Any, int, int, int) -> None
        """
        记录功能性方块的世界坐标。

        只登记落在调色板允许位置上的方块: 藏在结构内部(比如空腔里)的接口不算数,
        于是 `GetMachine()` / `GetAllMachines()` 也拿不到它。
        """
        allowed_pose_sets = self.rotated_palette.get_allowed_pose_sets()
        functional_block_poses = {}  # type: dict[str, list[tuple[int, int, int]]]
        for block_id in self.bound.functional_block_ids:
            allowed_poses = allowed_pose_sets.get(block_id)
            poses = []  # type: list[tuple[int, int, int]]
            if allowed_poses:
                for x, y, z in palette.GetLocalPosListOfBlocks(block_id):
                    if (x - co_x, y - co_y, z - co_z) in allowed_poses:
                        poses.append((
                            x - co_x + self.center_x,
                            y - co_y + self.center_y,
                            z - co_z + self.center_z,
                        ))
            functional_block_poses[block_id] = poses
        self.functional_block_poses = functional_block_poses

    def get_box(self):
        return (
            (self.min_x, self.min_y, self.min_z),
            (self.max_x, self.max_y, self.max_z),
        )

    def _detect_structure(self):
        spalette = self.rotated_palette
        current_palette = GetBlockPaletteBetweenPos(
            self.dim,
            (self.min_x, self.min_y, self.min_z),
            (self.max_x, self.max_y, self.max_z),
            eliminateAir=False,
        )
        if current_palette is None:
            logger.error("[Error] Palette is None")
            self.bound.lacked_block_poses = []
            return DEACTIVE_FLAG_STRUCTURE_BROKEN
        co_x = self.center_x - self.min_x
        co_y = self.center_y - self.min_y
        co_z = self.center_z - self.min_z
        actual_poses = spalette.collect_actual_poses(current_palette, co_x, co_y, co_z)
        if not spalette.compare(current_palette, co_x, co_y, co_z, actual_poses):
            # 结构还没搭全, 先报缺哪块, 不掺和"多了东西"的问题
            self.bound.lacked_block_poses = self._find_mismatch_poses(
                spalette, actual_poses
            )
            return DEACTIVE_FLAG_STRUCTURE_BROKEN
        lacked_blocks = spalette.get_lacked_blocks(current_palette, co_x, co_y, co_z)
        if lacked_blocks:
            self.bound.lacked_blocks = lacked_blocks
            if self.bound.lacked_block_poses:
                self.bound.lacked_block_poses = []
            return DEACTIVE_FLAG_STRUCTURE_BLOCK_LACK
        # 方块齐了, 再看有没有"不该有方块"的位置: 空腔被填 / 接口没放在允许的位置上
        foul_poses = self._find_foul_poses(spalette, current_palette, co_x, co_y, co_z)
        if foul_poses:
            self.bound.lacked_block_poses = foul_poses
            return DEACTIVE_FLAG_STRUCTURE_BROKEN
        self._update_functional_blocks(current_palette, co_x, co_y, co_z)
        return FLAG_OK

    def _make_mismatch_pose(self, x, y, z, expected_block_ids):
        # type: (int, int, int, list[str]) -> dict[str, object]
        "把核心相对坐标转成世界坐标, 并记下该位置实际是什么方块。"
        wx, wy, wz = x + self.center_x, y + self.center_y, z + self.center_z
        return {
            "x": wx,
            "y": wy,
            "z": wz,
            "expected": expected_block_ids,
            "actual": GetBlockName(self.dim, (wx, wy, wz)) or "",
        }

    def _find_mismatch_poses(self, spalette, actual_poses):
        # type: (StructureBlockPalette, dict[BLOCK_PAT_INDEX, POS_SET]) -> list[dict]
        """结构不完整时, 找出期望方块与当前方块不匹配的具体位置."""
        res = []
        for index, block_ids in sorted(spalette.palette_data.items()):
            if isinstance(block_ids, str):
                block_ids = [block_ids]
            expected_pos_set = spalette.posblock_data[index]
            for x, y, z in sorted(expected_pos_set - actual_poses.get(index, set())):
                res.append(self._make_mismatch_pose(x, y, z, block_ids))
                if len(res) >= MAX_STRUCTURE_MISMATCH_POSES:
                    return res
        return res

    def _find_foul_poses(self, spalette, current_palette, co_x, co_y, co_z):
        # type: (StructureBlockPalette, typing.Any, int, int, int) -> list[dict]
        """
        结构搭全之后, 找出"多了东西"的位置。

        两类: 图案里标成"必须为空"却被填上的位置, 以及没放在允许位置上的功能性方块
        (典型做法是把接口藏进结构内部)。结构搭全时, 调色板允许的位置上不可能再挤进第二个方块,
        所以空腔里的位置按"必须为空"上报, 放错的接口按"这个位置本来该放什么"上报。
        """
        res = []
        reported = set()  # type: POS_SET
        air_violations = spalette.get_occupied_air_poses(
            current_palette, co_x, co_y, co_z
        )
        for x, y, z in sorted(air_violations):
            reported.add((x, y, z))
            pose = self._make_mismatch_pose(x, y, z, [AIR_BLOCK_ID])
            if pose["actual"] == AIR_BLOCK_ID:
                # 调色板不一定统计空气, 以该位置实际的方块为准, 免得把好好的空腔误判成被填了
                continue
            res.append(pose)
            if len(res) >= MAX_STRUCTURE_MISMATCH_POSES:
                return res
        foul_pose_sets = spalette.get_disallowed_pose_sets(
            current_palette, co_x, co_y, co_z, self.bound.functional_block_ids
        )
        for block_id in sorted(foul_pose_sets):
            for x, y, z in sorted(foul_pose_sets[block_id]):
                if (x, y, z) in reported:
                    continue
                reported.add((x, y, z))
                expected = spalette.get_allowed_block_ids((x, y, z)) or [AIR_BLOCK_ID]
                res.append(self._make_mismatch_pose(x, y, z, expected))
                if len(res) >= MAX_STRUCTURE_MISMATCH_POSES:
                    return res
        return res

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


class MultiBlockStructure(BaseMachine):
    """
    多方块机器结构的基类。

    派生自: `BaseMachine`

    覆写:
        - `__init__`
        - `OnUnload`

    Class Attributes:
        structure_palette (StructureBlockPalette | None): 检测多方块结构完整性的结构调色板
        functional_block_ids (set[str]): 多方块结构中功能性方块的列表。GetMachine() 获取的机器方块 id 都需要被包含在其中。
    """

    structure_palette = None  # type: StructureBlockPalette | None
    "用于进行多方块完整性检测的多方块结构调色板。"
    functional_block_ids = set()  # type: set[str]
    """
    多方块结构中功能性方块的列表。

    这些方块必须放在结构调色板允许它们的位置上: 藏进结构内部(比如空腔里)的接口不会登记到
    `GetFunctionalBlockPoses()`, 而且会让结构直接判定为破损。
    """

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        if self.structure_palette is None:
            raise ValueError("StructureBlockPalette: structure_palette is None")
        self._last_destroy_flag = DEACTIVE_FLAG_STRUCTURE_BROKEN
        self._lacked_blocks = {}  # type: dict[str, int]
        self._lacked_block_poses = []  # type: list[dict[str, object]]
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
        if self.deactive_flags & STRUCTURE_DEACTIVE_FLAGS:
            self.deactive_flags &= ~STRUCTURE_DEACTIVE_FLAGS
        self.last_destroy_flag = flag
        self.area.functional_block_poses = {}
        if flag != DEACTIVE_FLAG_STRUCTURE_BLOCK_LACK:
            self.lacked_blocks = {}
        self.SetDeactiveFlag(flag)
        self.OnStructureChanged(False)
        if isinstance(self, GUIControl):
            self.CallSync()

    def UnsetStructureDestroyed(self):
        if (
            self.last_destroy_flag != FLAG_OK
            or self.deactive_flags & STRUCTURE_DEACTIVE_FLAGS
        ):
            if self.deactive_flags & STRUCTURE_DEACTIVE_FLAGS:
                self.deactive_flags &= ~STRUCTURE_DEACTIVE_FLAGS
                self.OnDeactiveFlagsChanged()
            self.last_destroy_flag = FLAG_OK
            self.lacked_blocks = {}
            self.lacked_block_poses = []
            self.FlushDeactiveFlags()
            self.OnStructureChanged(True)
            if isinstance(self, GUIControl):
                self.CallSync()

    def GetStructureDestroyFlag(self):
        return self.last_destroy_flag

    def GetStructureLackedBlocks(self):
        return self.lacked_blocks

    def GetStructureLackedBlockPoses(self):
        "返回缺失方块的具体位置列表, 每条为 (x, y, z, 期望方块, 实际方块) 组成的 dict."
        return self.lacked_block_poses

    def GetFunctionalBlockPoses(self):
        """
        返回功能性方块的世界坐标, 按方块 ID 分组, 结构完整时才会更新。

        只包含放在调色板允许位置上的方块, 藏在结构内部的接口不会出现在这里。
        """
        return self.area.functional_block_poses

    def StructureFinished(self):
        return self.last_destroy_flag == 0

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

    def _find_machine(self, cls, block_id, index):
        # type: (type[MT], str, int) -> tuple[MT | None, str]
        "查找功能性方块上的机器, 返回 (机器, 失败原因); 成功时失败原因为空字符串。"
        from ..pool import GetMachineStrict

        poses = self.GetFunctionalBlockPoses().get(block_id)
        if not poses:
            return None, "Cannot find block: %s" % block_id
        if index >= len(poses) or index < -len(poses):
            return None, "Index %d out of range: %s has %d pos" % (
                index,
                block_id,
                len(poses),
            )
        x, y, z = poses[index]
        machine = GetMachineStrict(self.dim, x, y, z)
        if not isinstance(machine, cls):
            return None, "({}, {}, {}): {} is not a {}".format(
                x, y, z, type(machine).__name__, cls.__name__
            )
        return machine, ""

    def GetMachine(self, cls, block_id=None, index=0):
        # type: (type[MT], str | None, int) -> MT
        """
        获取多方块结构中某一类型的机器(多用于多方块结构接口的获取)。
        其 ID 需要被包含在类属性 `functional_block_ids` 中。

        Args:
            cls (type[BaseMachine]): 机器类
            block_id (str, optional): 机器方块 ID。默认为 cls.block_name
            index (int, optional): 索引值, 如果有多个匹配的机器则使用索引值。

        Raises:
            ValueError: 找不到该方块的位置 / 索引越界 / 机器未加载 / 方块上的机器类型不符合 cls

        Returns:
            BaseMachine: 所求机器类
        """
        machine, error = self._find_machine(cls, block_id or cls.block_name, index)
        if machine is None:
            raise ValueError(error)
        return machine

    def TryGetMachine(self, cls, block_id=None, index=0):
        # type: (type[MT], str | None, int) -> MT | None
        """
        `GetMachine` 的可空返回版本: 方块位置缺失 / 索引越界 / 机器未加载 / 类型不符时返回 None,
        不会抛异常。
        """
        return self._find_machine(cls, block_id or cls.block_name, index)[0]

    @property
    def last_destroy_flag(self):
        # type: () -> int
        return self._last_destroy_flag

    @last_destroy_flag.setter
    def last_destroy_flag(self, value):
        # type: (int) -> None
        self.bdata[K_DESTROY_FLAG] = self._last_destroy_flag = value

    @property
    def lacked_blocks(self):
        # type: () -> dict[str, int]
        return self._lacked_blocks

    @lacked_blocks.setter
    def lacked_blocks(self, value):
        # type: (dict[str, int]) -> None
        value = value or {}
        self.bdata[K_STRUCTURE_LACKED_BLOCKS] = self._lacked_blocks = value

    @property
    def lacked_block_poses(self):
        # type: () -> list[dict[str, object]]
        return self._lacked_block_poses

    @lacked_block_poses.setter
    def lacked_block_poses(self, value):
        # type: (list[dict[str, object]]) -> None
        value = value or []
        self.bdata[K_STRUCTURE_LACKED_BLOCK_POSES] = self._lacked_block_poses = value


def get_chunks_in_range(startx, startz, endx, endz):
    # type: (int, int, int, int) -> set[tuple[int, int]]
    startx, endx = sorted([startx, endx])
    startz, endz = sorted([startz, endz])
    return {
        (x, z)
        for x in range(startx // 16, endx // 16 + 1)
        for z in range(startz // 16, endz // 16 + 1)
    }


def get_not_loaded_chunk_poses_in_range(dim, startx, startz, endx, endz):
    # type: (int, int, int, int, int) -> set[tuple[int, int]]
    res = set()  # type: set[tuple[int, int]]
    startx, endx = sorted([startx, endx])
    startz, endz = sorted([startz, endz])
    for x in range(startx // 16, endx // 16 + 1):
        for z in range(startz // 16, endz // 16 + 1):
            p = (x, z)
            if (dim, x, z) in loaded_chunks:
                continue
            res.add(p)
    return res


@ServerInitCallback()
def onServerInit():
    global server_inited
    AddBlocksToBlockRemoveListener(block_removed_listen_pool)
    server_inited = True


@ServerUninitCallback()
def onServerUninit():
    "卸载时清空待检测队列, 避免把过期的检测任务和标记带到下一次启动。"
    global flush_scheduled
    dirty_detect_areas.clear()
    flush_scheduled = False


@EntityPlaceBlockAfterServerEvent.Listen(0)
def onEntityPlaceStruBlock(event):
    # type: (EntityPlaceBlockAfterServerEvent) -> None
    x = event.x
    y = event.y
    z = event.z
    for area in tuple(detect_areas.get(event.dimensionId, set())):
        if not area.has_bound:
            drop_orphan_detect_area(area)
            continue
        # 结构健全时, 只有"可能多放东西"的方块值得重新检测:
        # 功能性方块放错位置, 或者往"必须为空"的位置里塞方块
        if (
            area.inited
            and area.bound._last_destroy_flag == FLAG_OK
            and event.fullName not in area.bound.functional_block_ids
            and (x, y, z) not in area.air_poses_in_world
        ):
            continue
        if area.is_inside(x, y, z):
            mark_detect_area_dirty(area)


@BlockRemoveServerEvent.Listen(1)
def onStruBlockRemoved(event):
    # type: (BlockRemoveServerEvent) -> None
    x = event.x
    y = event.y
    z = event.z
    for area in tuple(detect_areas.get(event.dimension, set())):
        if not area.has_bound:
            drop_orphan_detect_area(area)
            continue
        if (
            area.inited
            and area.bound._last_destroy_flag == DEACTIVE_FLAG_STRUCTURE_BROKEN
            and event.fullName not in area.bound.functional_block_ids
            and (x, y, z) not in area.air_poses_in_world
        ):
            # 拆结构方块救不回缺件的结构; 但拆掉乱塞的接口 / 空腔里的方块属于补救, 要重新检测
            continue
        if area.is_inside(x, y, z):
            if x == area.center_x and y == area.center_y and z == area.center_z:
                return
            # 事件触发时原方块还是原方块, 标记到下一 tick 检测时才变成空气
            mark_detect_area_dirty(area)


@ChunkLoadedServerEvent.Listen(-1001)
def onChunkLoaded(event):
    # type: (ChunkLoadedServerEvent) -> None
    pos = (event.dimension, event.chunkPosX, event.chunkPosZ)
    loaded_chunks.add(pos)
    areas = chunks_to_detect.get(event.dimension, {}).get(pos[1:])
    if areas is None:
        return
    for area in areas:
        area.add_loaded_chunk(pos[1:])


@ChunkAcquireDiscardedServerEvent.Listen(1001)
def onChunkDiscarded(event):
    # type: (ChunkAcquireDiscardedServerEvent) -> None
    pos = (event.dimension, event.chunkPosX, event.chunkPosZ)
    loaded_chunks.discard(pos)
    areas = chunks_to_detect.get(event.dimension, {}).get(pos[1:])
    if areas is None:
        return
    for area in areas:
        area.discard_loaded_chunk(pos[1:])


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
if False:
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
