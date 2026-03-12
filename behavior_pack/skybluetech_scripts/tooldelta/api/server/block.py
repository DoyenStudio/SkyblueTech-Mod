# coding=utf-8

from mod.common.component.blockPaletteComp import BlockPaletteComponent
from ...define.block import BlockBasicInfo
from ...internal import ServerComp, ServerLevelId
from ..internal.cacher import MethodCacher

if 0:
    from mod.server.blockEntityData import BlockEntityData

_getBlockNew = MethodCacher(
    lambda: ServerComp.CreateBlockInfo(ServerLevelId).GetBlockNew
)
_getBlockEntityData = MethodCacher(
    lambda: ServerComp.CreateBlockEntityData(ServerLevelId).GetBlockEntityData
)
_getBlockEntityDict = MethodCacher(
    lambda: ServerComp.CreateBlockInfo(ServerLevelId).GetBlockEntityData
)
_getBlockTags = MethodCacher(
    lambda: ServerComp.CreateBlockInfo(ServerLevelId).GetBlockTags
)
_getBlockStates = MethodCacher(
    lambda: ServerComp.CreateBlockState(ServerLevelId).GetBlockStates
)
_getBlockBasicInfo = MethodCacher(
    lambda: ServerComp.CreateBlockInfo(ServerLevelId).GetBlockBasicInfo
)
_getLiquidBlock = MethodCacher(
    lambda: ServerComp.CreateBlockInfo(ServerLevelId).GetLiquidBlock
)
_listenOnBlockRemoveEvent = MethodCacher(
    lambda: ServerComp.CreateBlockInfo(ServerLevelId).ListenOnBlockRemoveEvent
)
_setBlockStates = MethodCacher(
    lambda: ServerComp.CreateBlockState(ServerLevelId).SetBlockStates
)
_setBlockNew = MethodCacher(
    lambda: ServerComp.CreateBlockInfo(ServerLevelId).SetBlockNew
)
_setLiquidBlock = MethodCacher(
    lambda: ServerComp.CreateBlockInfo(ServerLevelId).SetLiquidBlock
)


def GetBlockEntityDataDict(dim, xyz):
    # type: (int, tuple[int, int, int]) -> dict | None
    return _getBlockEntityDict(dim, xyz)


def GetBlockEntityData(dim, xyz):
    # type: (int, tuple[int, int, int]) -> BlockEntityData | None
    return _getBlockEntityData(dim, xyz)


block_tags_cache = {}  # type: dict[str, set[str]]


def GetBlockTags(block_name):
    # type: (str) -> set[str]
    if block_name in block_tags_cache:
        return block_tags_cache[block_name]
    else:
        tags = block_tags_cache[block_name] = set(_getBlockTags(block_name))
        return tags


block_basic_info_cache = {}  # type: dict[str, BlockBasicInfo]


def GetBlockBasicInfo(block_name):
    # type: (str) -> BlockBasicInfo
    if block_name in block_basic_info_cache:
        return block_basic_info_cache[block_name]
    else:
        info = block_basic_info_cache[block_name] = BlockBasicInfo.unmarshal(
            _getBlockBasicInfo(block_name)
        )
        return info


def GetPosBlockTags(dim, pos):
    # type: (int, tuple[int, int, int]) -> set[str] | None
    bname = GetBlockName(dim, pos)
    if bname is None:
        return None
    return GetBlockTags(bname)


def BlockHasTag(block_name, tag):
    # type: (str, str) -> bool
    return tag in GetBlockTags(block_name)


def GetBlockName(dim, pos):
    # type: (int, tuple[int, int, int]) -> str | None
    b = _getBlockNew(pos, dim)
    if b is None:
        return None
    else:
        return b["name"]


def GetBlockNameAndAux(dim, pos):
    # type: (int, tuple[int, int, int]) -> tuple[str | None, int]
    b = _getBlockNew(pos, dim)
    if b is None:
        return None, 0
    else:
        return b["name"], b["aux"]


def GetLiquidBlock(dim, pos):
    # type: (int, tuple[int, int, int]) -> tuple[str | None, int]
    b = _getLiquidBlock(pos, dim)
    if b is None:
        return None, 0
    else:
        return b["name"], b["aux"]


def SetBlock(dim, pos, block_name, aux_value=0, old_block_handing=0):
    # type: (int, tuple[int, int, int], str, int, int) -> bool
    return _setBlockNew(
        pos, {"name": block_name, "aux": aux_value}, old_block_handing, dimensionId=dim
    )


def SetLiquidBlock(dim, pos, block_name, aux_value=0):
    # type: (int, tuple[int, int, int], str, int) -> bool
    return _setLiquidBlock(pos, {"name": block_name, "aux": aux_value}, dimensionId=dim)


def GetBlockStates(dim, pos):
    # type: (int, tuple[int, int, int]) -> dict
    return _getBlockStates(pos, dim)


def GetBlockCardinalFacing(dim, pos):
    # type: (int, tuple[int, int, int]) -> str
    return _getBlockStates(pos, dim)["minecraft:cardinal_direction"]


def GetBlockFacingDir(dim, pos):
    # type: (int, tuple[int, int, int]) -> str
    return _getBlockStates(pos, dim)["minecraft:facing_direction"]


def UpdateBlockStates(dim, pos, states, prev_states=None):
    # type: (int, tuple[int, int, int], dict, dict | None) -> bool
    if prev_states is None:
        prev_states = _getBlockStates(pos, dim)
    prev_states.update(states)
    return _setBlockStates(pos, prev_states, dim)


def AddBlocksToBlockRemoveListener(blocks):
    # type: (set[str]) -> None
    for block in blocks:
        _listenOnBlockRemoveEvent(block, True)


_CARDINAL_FACING = {"north": 0, "west": 1, "south": 2, "east": 3}


def GetActualFacingByCardinalFacing(cardinal_direction, origin_facing):
    # type: (str, int) -> int
    if origin_facing < 2:
        return origin_facing
    return (origin_facing + _CARDINAL_FACING[cardinal_direction]) % 4


def GetActualFacingByDirection(direction, origin_facing):
    # type: (int, int) -> int
    if origin_facing < 2:
        return origin_facing
    return (origin_facing + direction - 2) % 4


def NewSingleBlockPalette(block_id):
    # type: (str) -> BlockPaletteComponent
    newBlockPalette = ServerComp.CreateBlock(ServerLevelId).GetBlankBlockPalette()
    newBlockPalette.DeserializeBlockPalette({
        "extra": {},
        "void": False,
        "actor": {},
        "volume": (1, 1, 1),
        "common": {(block_id, 0): [0]},
        "eliminateAir": True,
    })
    return newBlockPalette


GetBlockPaletteFromPosList = MethodCacher(
    lambda: ServerComp.CreateBlock(ServerLevelId).GetBlockPaletteFromPosList
)
GetBlockPaletteBetweenPos = MethodCacher(
    lambda: ServerComp.CreateBlock(ServerLevelId).GetBlockPaletteBetweenPos
)
GetTopBlockHeight = MethodCacher(
    lambda: ServerComp.CreateBlockInfo(ServerLevelId).GetTopBlockHeight
)
GetBlockAuxValueFromStates = MethodCacher(
    lambda: ServerComp.CreateBlockState(ServerLevelId).GetBlockAuxValueFromStates
)
GetBlockStatesFromAuxValue = MethodCacher(
    lambda: ServerComp.CreateBlockState(ServerLevelId).GetBlockStatesFromAuxValue
)
MayPlace = MethodCacher(lambda: ServerComp.CreateBlockInfo(ServerLevelId).MayPlace)


__all__ = [
    "AddBlocksToBlockRemoveListener",
    "GetBlockEntityData",
    "GetBlockEntityDataDict",
    "GetBlockTags",
    "GetBlockBasicInfo",
    "GetPosBlockTags",
    "GetTopBlockHeight",
    "GetLiquidBlock",
    "GetBlockAuxValueFromStates",
    "GetBlockStatesFromAuxValue",
    "GetBlockPaletteFromPosList",
    "GetBlockPaletteBetweenPos",
    "GetBlockCardinalFacing",
    "GetBlockName",
    "BlockHasTag",
    "MayPlace",
    "SetBlock",
    "SetLiquidBlock",
    "GetBlockStates",
    "UpdateBlockStates",
]
