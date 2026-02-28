# coding=utf-8
#
from skybluetech_scripts.tooldelta.api.server.block import (
    GetBlockStates as _getBlockStates,
    GetActualFacingByCardinalFacing as _getActualFacing,
    GetActualFacingByDirection as _getActualFacing2
)

def FixIOModeByCardinalFacing(dim, x, y, z, origin):
    # type: (int, int, int, int, tuple[int, int, int, int, int, int]) -> tuple[int, int, int, int, int, int]
    cardinal_facing = _getBlockStates(dim, (x, y, z))["minecraft:cardinal_direction"]
    new_iomodes = [0, 0, 0, 0, 0, 0]
    for origin_facing, origin_mode in enumerate(origin):
        new_iomodes[_getActualFacing(cardinal_facing, origin_facing)] = origin_mode
    return tuple(new_iomodes) # pyright: ignore[reportReturnType]

def FixIOModeByDirection(dim, x, y, z, origin):
    # type: (int, int, int, int, tuple[int, int, int, int, int, int]) -> tuple[int, int, int, int, int, int]
    states = _getBlockStates(dim, (x, y, z))
    direction = states["direction"]
    new_iomodes = [0, 0, 0, 0, 0, 0]
    for origin_facing, origin_mode in enumerate(origin):
        new_iomodes[_getActualFacing2(direction, origin_facing)] = origin_mode
    return tuple(new_iomodes) # pyright: ignore[reportReturnType]

