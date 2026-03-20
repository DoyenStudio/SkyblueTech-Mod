# coding=utf-8
from mod.server.blockEntityData import BlockEntityData
from mod.server.extraServerApi import GetEngineCompFactory, GetLevelId
from ...define.block import BlockBasicInfo
from ..common.cacher import MethodCacher

CF = GetEngineCompFactory()

_getBlockNew = MethodCacher(lambda: CF.CreateBlockInfo(GetLevelId()).GetBlockNew)
_getBlockEntityData = MethodCacher(
    lambda: CF.CreateBlockEntityData(GetLevelId()).GetBlockEntityData
)
_getBlockEntityDict = MethodCacher(
    lambda: CF.CreateBlockInfo(GetLevelId()).GetBlockEntityData
)
_getBlockTags = MethodCacher(lambda: CF.CreateBlockInfo(GetLevelId()).GetBlockTags)
_getBlockStates = MethodCacher(lambda: CF.CreateBlockState(GetLevelId()).GetBlockStates)
_getBlockBasicInfo = MethodCacher(
    lambda: CF.CreateBlockInfo(GetLevelId()).GetBlockBasicInfo
)
_getLiquidBlock = MethodCacher(lambda: CF.CreateBlockInfo(GetLevelId()).GetLiquidBlock)
_listenOnBlockRemoveEvent = MethodCacher(
    lambda: CF.CreateBlockInfo(GetLevelId()).ListenOnBlockRemoveEvent
)
_setBlockStates = MethodCacher(lambda: CF.CreateBlockState(GetLevelId()).SetBlockStates)
_setBlockNew = MethodCacher(lambda: CF.CreateBlockInfo(GetLevelId()).SetBlockNew)
_setLiquidBlock = MethodCacher(lambda: CF.CreateBlockInfo(GetLevelId()).SetLiquidBlock)
_setBlockEntityData = MethodCacher(
    lambda: CF.CreateBlockInfo(GetLevelId()).SetBlockEntityData
)

def GetBlockEntityDataDict(dim: int, xyz: tuple[int, int, int]) -> dict | None:
    return _getBlockEntityDict(dim, xyz)

def GetBlockEntityData(dim: int, xyz: tuple[int, int, int]) -> BlockEntityData | None:
    return _getBlockEntityData(dim, xyz)

def SetBlockEntityData(dim: int, xyz: tuple[int, int, int], data: dict) -> None:
    _setBlockEntityData(dim, xyz, data)

block_tags_cache: dict[str, set[str]] = {}

def GetBlockTags(block_name: str) -> set[str]:
    if block_name in block_tags_cache:
        return block_tags_cache[block_name]
    else:
        tags = block_tags_cache[block_name] = set(_getBlockTags(block_name))
        return tags

block_basic_info_cache: dict[str, BlockBasicInfo] = {}

def GetBlockBasicInfo(block_name: str) -> BlockBasicInfo:
    if block_name in block_basic_info_cache:
        return block_basic_info_cache[block_name]
    else:
        info = block_basic_info_cache[block_name] = BlockBasicInfo.unmarshal(
            _getBlockBasicInfo(block_name)
        )
        return info

def GetPosBlockTags(dim: int, pos: tuple[int, int, int]) -> set[str] | None: ...
def BlockHasTag(block_name: str, tag: str) -> bool:
    return tag in GetBlockTags(block_name)

def GetBlockName(dim: int, pos: tuple[int, int, int]) -> str | None:
    b = _getBlockNew(pos, dim)
    if b is None:
        return None
    else:
        return b["name"]

def GetBlockNameAndAux(dim: int, pos: tuple[int, int, int]) -> tuple[str | None, int]:
    b = _getBlockNew(pos, dim)
    if b is None:
        return None, 0
    else:
        return b["name"], b["aux"]

def GetLiquidBlock(dim: int, pos: tuple[int, int, int]) -> tuple[str | None, int]:
    b = _getLiquidBlock(pos, dim)
    if b is None:
        return None, 0
    else:
        return b["name"], b["aux"]

def SetBlock(
    dim: int,
    pos: tuple[int, int, int],
    block_name: str,
    aux_value: int = 0,
    old_block_handing: int = 0,
) -> bool:
    return _setBlockNew(
        pos, {"name": block_name, "aux": aux_value}, old_block_handing, dimensionId=dim
    )

def SetLiquidBlock(
    dim: int, pos: tuple[int, int, int], block_name: str, aux_value: int = 0
) -> bool:
    return _setLiquidBlock(pos, {"name": block_name, "aux": aux_value}, dimensionId=dim)

def GetBlockStates(dim: int, pos: tuple[int, int, int]) -> dict:
    return _getBlockStates(pos, dim)

def GetBlockCardinalFacing(dim: int, pos: tuple[int, int, int]) -> str:
    return _getBlockStates(pos, dim)["minecraft:cardinal_direction"]

def GetBlockFacingDir(dim: int, pos: tuple[int, int, int]) -> str:
    return _getBlockStates(pos, dim)["minecraft:facing_direction"]

def UpdateBlockStates(
    dim: int, pos: tuple[int, int, int], states: dict, prev_states: dict | None = None
) -> bool: ...
def AddBlocksToBlockRemoveListener(blocks: set[str]) -> None:
    for block in blocks:
        _listenOnBlockRemoveEvent(block, True)

_CARDINAL_FACING: dict[str, int] = {"north": 0, "west": 1, "south": 2, "east": 3}

def GetActualFacingByCardinalFacing(cardinal_direction: str, origin_facing: int) -> int:
    if origin_facing < 2:
        return origin_facing
    return (origin_facing + _CARDINAL_FACING[cardinal_direction]) % 4

def GetActualFacingByDirection(direction: int, origin_facing: int) -> int:
    if origin_facing < 2:
        return origin_facing
    return (origin_facing + direction - 2) % 4

def NewSingleBlockPalette(
    block_id: str,
):
    newBlockPalette = CF.CreateBlock(GetLevelId()).GetBlankBlockPalette()
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
    lambda: CF.CreateBlock(GetLevelId()).GetBlockPaletteFromPosList
)
GetBlockPaletteBetweenPos = MethodCacher(
    lambda: CF.CreateBlock(GetLevelId()).GetBlockPaletteBetweenPos
)
GetTopBlockHeight = MethodCacher(
    lambda: CF.CreateBlockInfo(GetLevelId()).GetTopBlockHeight
)
GetBlockAuxValueFromStates = MethodCacher(
    lambda: CF.CreateBlockState(GetLevelId()).GetBlockAuxValueFromStates
)
GetBlockStatesFromAuxValue = MethodCacher(
    lambda: CF.CreateBlockState(GetLevelId()).GetBlockStatesFromAuxValue
)
MayPlace = MethodCacher(lambda: CF.CreateBlockInfo(GetLevelId()).MayPlace)

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
    "GetBlockNameAndAux",
    "GetBlockStates",
    "BlockHasTag",
    "MayPlace",
    "SetBlock",
    "SetLiquidBlock",
    "SetBlockEntityData",
    "UpdateBlockStates",
]
