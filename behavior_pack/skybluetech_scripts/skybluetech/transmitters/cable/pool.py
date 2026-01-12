# coding=utf-8
#
from weakref import WeakValueDictionary as WValueDict


# TYPE_CHECKING
if 0:
    from .define import CableNetwork, CableAccessPoint
    DmPosData = tuple[int, tuple[int, int, int]]
# TYPE_CHECKING END


# TODO: 我的山头: 需要 GC
CableNetworkPool = {} # type: dict[DmPosData, tuple[list[CableNetwork], list[CableNetwork]]]
CableAccessPointPool = WValueDict() # type: WValueDict[tuple[int, int, int, int, int], CableAccessPoint] # (dim, x, y, z, access_facing)
GNodes = {} # type: dict[int, WValueDict[tuple[int, int, int], CableNetwork]]
