# coding=utf-8
if 0:
    from typing import Any

    BLOCK_PAT_INDEX = int
    POS_SET = set[tuple[int, int, int]]


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
                # if DEBUG:
                #     debug_show_diff(
                #         dim, cx, cy, cz, expected_pos_set, actua_pos_set, block_ids
                #     )
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


def rotate_90(x, z, center_x, center_z, y):
    # type: (int, int, int, int, int) -> tuple[int, int, int]
    dx = x - center_x
    dz = z - center_z
    return (center_x + dz, y, center_z - dx)
