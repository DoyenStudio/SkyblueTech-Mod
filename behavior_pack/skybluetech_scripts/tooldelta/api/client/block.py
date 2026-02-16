# coding=utf-8
from mod.common.component.blockPaletteComp import BlockPaletteComponent
from mod.client import extraClientApi as clientApi
from ...internal import ClientComp, ClientLevelId
from ..internal.cacher import MethodCacher


_getBlock = MethodCacher(lambda: ClientComp.CreateBlockInfo(ClientLevelId).GetBlock)
_getBlockEntityData = MethodCacher(
    lambda: ClientComp.CreateBlockInfo(ClientLevelId).GetBlockEntityData
)
_getBlockTextures = MethodCacher(
    lambda: ClientComp.CreateBlockInfo(ClientLevelId).GetBlockTextures
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


GetBlockTextures = _getBlockTextures


def NewSingleBlockPalette(block_id, aux=0):
    # type: (str, int) -> BlockPaletteComponent
    newBlockPalette = ClientComp.CreateBlock(ClientLevelId).GetBlankBlockPalette()
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
    blockGeometryComp = clientApi.GetEngineCompFactory().CreateBlockGeometry(
        ClientLevelId
    )
    return blockGeometryComp.CombineBlockPaletteToGeometry(palette, geo_name)


def AddBlockUseListener(block_ids):
    # type: (set[str]) -> None
    comp = ClientComp.CreateBlockUseEventWhiteList(ClientLevelId)
    for block_id in block_ids:
        comp.AddBlockItemListenForUseEvent(block_id)


SetBlockEntityMolangValue = MethodCacher(
    lambda: ClientComp.CreateBlockInfo(ClientLevelId).SetBlockEntityMolangValue
)
SetCrackFrame = MethodCacher(
    lambda: ClientComp.CreateBlockInfo(ClientLevelId).SetCrackFrame
)


__all__ = [
    "GetBlockName",
    "GetBlockNameAndAux",
    "GetBlockEntityData",
    "GetBlockTextures",
    "NewSingleBlockPalette",
    "CombineBlockPaletteToGeometry",
    "AddBlockUseListener",
    "SetBlockEntityMolangValue",
    "SetCrackFrame",
]
