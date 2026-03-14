# coding=utf-8
from mod.common.component.blockPaletteComp import BlockPaletteComponent
from mod.client.extraClientApi import GetEngineCompFactory, GetLevelId
from ..common.cacher import MethodCacher

CF = GetEngineCompFactory()

_getBlock = MethodCacher(lambda: CF.CreateBlockInfo(GetLevelId()).GetBlock)
_getBlockEntityData = MethodCacher(
    lambda: CF.CreateBlockInfo(GetLevelId()).GetBlockEntityData
)
_getBlockTextures = MethodCacher(
    lambda: CF.CreateBlockInfo(GetLevelId()).GetBlockTextures
)


def GetBlockEntityData(x, y, z):
    # type: (int, int, int) -> dict | None
    return _getBlockEntityData((x, y, z))


block_tags_cache = {}  # type: dict[str, set[str]]


def GetBlockName(pos):
    # type: (tuple[int, int, int]) -> str | None
    b = _getBlock(pos)
    if b is None:
        return None
    else:
        return b[0]


def GetBlockNameAndAux(pos):
    # type: (tuple[int, int, int]) -> tuple[str | None, int]
    b = _getBlock(pos)
    if b is None:
        return None, 0
    else:
        return b


def NewSingleBlockPalette(block_id, aux=0):
    # type: (str, int) -> BlockPaletteComponent
    newBlockPalette = GetBlankBlockPalette()
    newBlockPalette.DeserializeBlockPalette({
        "extra": {},
        "void": False,
        "actor": {},
        "volume": (1, 1, 1),
        "common": {(block_id, aux): [0]},
        "eliminateAir": True,
    })
    return newBlockPalette


def CombineBlockPaletteToGeometry(palette, geo_name):
    # type: (BlockPaletteComponent, str) -> str
    blockGeometryComp = GetEngineCompFactory().CreateBlockGeometry(GetLevelId())
    return blockGeometryComp.CombineBlockPaletteToGeometry(palette, geo_name)


def AddBlockUseListener(block_ids):
    # type: (set[str]) -> None
    comp = CF.CreateBlockUseEventWhiteList(GetLevelId())
    for block_id in block_ids:
        comp.AddBlockItemListenForUseEvent(block_id)


GetBlockTextures = _getBlockTextures
GetBlankBlockPalette = MethodCacher(
    lambda: CF.CreateBlock(GetLevelId()).GetBlankBlockPalette
)
GetBlockPaletteFromPosList = MethodCacher(
    lambda: CF.CreateBlock(GetLevelId()).GetBlockPaletteFromPosList
)
GetBlockPaletteBetweenPos = MethodCacher(
    lambda: CF.CreateBlock(GetLevelId()).GetBlockPaletteBetweenPos
)
SetBlockEntityMolangValue = MethodCacher(
    lambda: CF.CreateBlockInfo(GetLevelId()).SetBlockEntityMolangValue
)
SetCrackFrame = MethodCacher(lambda: CF.CreateBlockInfo(GetLevelId()).SetCrackFrame)

__all__ = [
    "GetBlankBlockPalette",
    "GetBlockName",
    "GetBlockNameAndAux",
    "GetBlockEntityData",
    "GetBlockTextures",
    "GetBlockPaletteBetweenPos",
    "GetBlockPaletteFromPosList",
    "NewSingleBlockPalette",
    "CombineBlockPaletteToGeometry",
    "AddBlockUseListener",
    "SetBlockEntityMolangValue",
    "SetCrackFrame",
]
