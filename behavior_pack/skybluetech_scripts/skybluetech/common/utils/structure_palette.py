# coding=utf-8
if 0>1:
    import typing

    BLOCK_PAT_INDEX = int
    POS_SET = typing.Set[typing.Tuple[int, int, int]]
    POS_LIST = typing.List[typing.Tuple[int, int, int]]


AIR_BLOCK_ID = "minecraft:air"
"空气方块 ID; 图案里标记为'必须为空'的位置在结构提示里就显示成它。"


class StructureBlockPalette(object):
    """
    多方块检测调色板, 用于表示多方块结构的内容。
    核心方块总是在内部坐标 `(0, 0, 0)` 处。

    注意: 核心只能朝北面放置, 也就是说朝向玩家的那面为南面。
    """

    # `require_blocks_count` 只统计**出现在调色板允许它的位置**上的方块数量, 所以把方块塞进
    # 结构内部是顶不了数量要求的。它用于给"可选族"(一个 index 对应多种方块)钉死必需的方块,
    # 比如"这一圈外壳上必须有 1 个能量接口"。

    # `air_poses` 记录图案里标成"必须为空"(`GenerateSimpleStructureTemplate()` 的 `air_block_sign`)
    # 的位置, 这些位置必须是空气, 用来禁止把方块(尤其是接口方块)藏进结构内部的空腔。

    # 坐标约定:
    #     本调色板中的所有坐标都是相对核心方块 `(0, 0, 0)` 的; 而 ModAPI
    #     `BlockPaletteComponent.GetLocalPosListOfBlocks()` 返回的是以查询区域最小坐标为原点的
    #     相对坐标, 两者相差核心方块在查询区域内的偏移, 也就是 `compare()` 等方法的 `co_*` 参数。
    

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
        air_poses=None,  # type: set[tuple[int, int, int]] | None
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
        self.air_poses = air_poses or set()  # type: POS_SET
        self._check_require_blocks()

    def _check_require_blocks(self):
        # type: () -> None
        "`require_blocks_count` 里的方块必须存在于调色板中, 否则结构永远不可能完整。"
        for block_id in self.require_blocks_count:
            if not any(
                block_id in self._to_block_ids(block_ids)
                for block_ids in self.palette_data.values()
            ):
                raise ValueError(
                    "require_blocks_count: block %s is not in palette" % block_id
                )

    @staticmethod
    def _to_block_ids(block_ids):
        # type: (str | list[str] | tuple[str, ...]) -> tuple[str, ...]
        "把 `palette_data` 的值(方块 ID 或可选族)统一成方块 ID 元组。"
        if isinstance(block_ids, str):
            return (block_ids,)
        return tuple(block_ids)

    def collect_actual_poses(self, block_palette, co_x, co_y, co_z):
        # type: (typing.Any, int, int, int) -> dict[BLOCK_PAT_INDEX, POS_SET]
        # 汇总每个 index 上实际方块的核心相对坐标。

        # `palette_data` 一个 index 可以对应多种方块(可选族), 这里把它们的位置取并集, 因此返回值
        # 可以直接用来判断"期望位置有没有被填上"。检测时算一次就够, 可以给 `compare()` 和
        # 查找不匹配位置的地方复用。
        res = {}
        for index, block_ids in self.palette_data.items():
            poses = set()  # type: POS_SET
            for block_id in self._to_block_ids(block_ids):
                for x, y, z in block_palette.GetLocalPosListOfBlocks(block_id):
                    poses.add((x - co_x, y - co_y, z - co_z))
            res[index] = poses
        return res

    def get_allowed_pose_sets(self):
        # type: () -> dict[str, POS_SET]
        # 返回调色板中每种方块**被允许出现**的核心相对坐标集合。

        # 一个 index 可以对应多种方块(可选族), 同一种方块也可能被多个 index 允许, 这里取并集。
        # "允许位置"是数量要求(``get_lacked_blocks()``)、接口取位和"藏方块"判定共用的唯一依据。
        res = {}
        for index, block_ids in self.palette_data.items():
            poses = self.posblock_data[index]
            for block_id in self._to_block_ids(block_ids):
                res.setdefault(block_id, set()).update(poses)
        return res

    def get_allowed_block_ids(self, pose):
        # type: (tuple[int, int, int]) -> list[str]
        # 返回某个位置上允许出现的方块 ID 列表(已排序); 空列表表示调色板不管这个位置。

        # 用于给"方块放错位置"的提示配文: 告诉玩家这个位置本来该放什么。
        block_ids = set()  # type: set[str]
        for index, expected_pos_set in self.posblock_data.items():
            if pose in expected_pos_set:
                block_ids.update(self._to_block_ids(self.palette_data.get(index, ())))
        return sorted(block_ids)

    def get_placed_pose_sets(self, block_palette, co_x, co_y, co_z, block_ids):
        # type: (typing.Any, int, int, int, typing.Iterable[str]) -> dict[str, POS_SET]
        # 返回这些方块在检测到的调色板中的实际位置(核心相对坐标)。
        return {
            block_id: {
                (x - co_x, y - co_y, z - co_z)
                for x, y, z in block_palette.GetLocalPosListOfBlocks(block_id)
            }
            for block_id in block_ids
        }

    def get_disallowed_pose_sets(self, block_palette, co_x, co_y, co_z, block_ids):
        # type: (typing.Any, int, int, int, typing.Iterable[str]) -> dict[str, POS_SET]
        # 返回这些方块中**出现在调色板不允许的位置**上的位置(核心相对坐标)。

        # 用于拒绝"把接口方块藏进结构内部"这种做法: 藏起来的方块不算结构的一部分。
        # 调色板里压根没有的方块 ID 直接跳过(它在哪儿都不算数, 也就谈不上放错位置)。
        allowed_pose_sets = self.get_allowed_pose_sets()
        placed_pose_sets = self.get_placed_pose_sets(
            block_palette, co_x, co_y, co_z, block_ids
        )
        return {
            block_id: placed_pose_sets[block_id] - allowed_pose_sets[block_id]
            for block_id in block_ids
            if block_id in allowed_pose_sets
        }

    def get_occupied_air_poses(self, block_palette, co_x, co_y, co_z):
        # type: (typing.Any, int, int, int) -> POS_SET
        # 返回图案里标成"必须为空"、当前却摆着方块的位置(核心相对坐标)。

        # 用于禁止把方块(尤其是接口方块)塞进结构内部的空腔。检测用的 `block_palette` 必须以
        # `eliminateAir=False` 取得, 否则空气方块根本不在调色板里, 这里也就无从判断谁被填上了。
        if not self.air_poses:
            return set()
        air_poses = {
            (x - co_x, y - co_y, z - co_z)
            for x, y, z in block_palette.GetLocalPosListOfBlocks(AIR_BLOCK_ID)
        }
        return self.air_poses - air_poses

    def compare(self, block_palette, co_x, co_y, co_z, actual_poses=None):
        # type: (typing.Any, int, int, int, dict[BLOCK_PAT_INDEX, POS_SET] | None) -> bool
        """
        比较方块调色板内容是否与此调色板匹配。

        Args:
            block_palette (BlockPaletteComponent): 调色板
            co_x (int): 核心方块在 `block_palette` 中的相对坐标 x
            co_y (int): 核心方块在 `block_palette` 中的相对坐标 y
            co_z (int): 核心方块在 `block_palette` 中的相对坐标 z
            actual_poses (dict[int, set[tuple[int, int, int]]] | None): `collect_actual_poses()`
                的结果, 传入可省掉一次重复查询

        只检查期望位置有没有被填上, 多出来的方块不影响匹配结果。
        """
        if actual_poses is None:
            actual_poses = self.collect_actual_poses(block_palette, co_x, co_y, co_z)
        for index, expected_pos_set in self.posblock_data.items():
            if not expected_pos_set.issubset(actual_poses.get(index, ())):
                return False
        return True

    def get_lacked_blocks(self, block_palette, co_x, co_y, co_z):
        # type: (typing.Any, int, int, int) -> dict[str, int]
        # 返回 `require_blocks_count` 中每种方块**还差的数量**, 全部满足时返回空 dict。
        # 只有落在"允许该方块的位置"上的方块才算数, 藏在结构内部的不算。
        allowed_pose_sets = self.get_allowed_pose_sets()
        placed_pose_sets = self.get_placed_pose_sets(
            block_palette, co_x, co_y, co_z, self.require_blocks_count
        )
        res = {}
        for block_id, require_count in self.require_blocks_count.items():
            placed_poses = placed_pose_sets[block_id] & allowed_pose_sets[block_id]
            missing_count = require_count - len(placed_poses)
            if missing_count > 0:
                res[block_id] = missing_count
        return res

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
        new_air_poses = {
            rotate_90(x, z, 0, 0, y) for x, y, z in self.air_poses
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
            new_air_poses,
        )


def GenerateSimpleStructureTemplate(
    key,  # type: dict[str, str] | dict[str, str | list[str]]
    pattern,  # type: dict[int, list[str]]
    center_block_sign="#",  # type: str
    require_blocks_count=None,  # type: dict[str, int] | None
    air_block_sign=".",  # type: str
):
    # type: (...) -> StructureBlockPalette
    """
    由文本图案生成结构调色板。

    Args:
        key (dict[str, str | list[str]]): 单字母键 -> 方块 ID; 值也可以是方块 ID 列表,
            表示"这些方块放在这个字母的位置上都行"。
        pattern (dict[int, list[str]]): 层号 -> 该层的行字符串列表, 行对应 z, 列对应 x。
        center_block_sign (str): 核心方块在图案中的标记, 有且只能有一个; 核心方块固定在内部坐标
            `(0, 0, 0)`, 本身不参与检测。
        require_blocks_count (dict[str, int] | None): 额外要求: 这些方块必须出现在调色板允许它的
            位置上, 且数量不少于给定值。
        air_block_sign (str): 图案中表示"这里必须是空气"的标记, 用于禁止把方块(尤其是接口方块)
            藏进结构内部的空腔; 该位置也会被算进检测范围。

    图案中的空格表示"不关心", 不会参与检测, 可以放任何方块。
    """
    orig_posblock_data = {}  # type: dict[BLOCK_PAT_INDEX, POS_SET]
    air_orig_poses = set()  # type: POS_SET
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
                if pat == air_block_sign:
                    air_orig_poses.add((x, layer, z))
                    continue
                if pat == center_block_sign:
                    if offset_x is not None:
                        raise ValueError(
                            "Multiple %s in pattern" % center_block_sign
                        )
                    offset_x = x
                    offset_y = layer
                    offset_z = z
                    continue
                idx = get_index_by_pattern(pat)
                orig_posblock_data.setdefault(idx, set()).add((x, layer, z))

    if offset_x is None or offset_y is None or offset_z is None:
        raise ValueError("No %s in pattern" % center_block_sign)

    posblock_data = {
        k: {(x - offset_x, y - offset_y, z - offset_z) for x, y, z in v}
        for k, v in orig_posblock_data.items()
    }
    air_poses = {
        (x - offset_x, y - offset_y, z - offset_z) for x, y, z in air_orig_poses
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
        air_poses,
    )


def rotate_90(x, z, center_x, center_z, y):
    # type: (int, int, int, int, int) -> tuple[int, int, int]
    dx = x - center_x
    dz = z - center_z
    return (center_x + dz, y, center_z - dx)
