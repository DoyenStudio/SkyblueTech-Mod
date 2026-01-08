# coding=utf-8
#
from weakref import WeakValueDictionary as WValueDict
from ....tooldelta.no_runtime_typing import TYPE_CHECKING

# TYPE_CHECKING
if TYPE_CHECKING:
    from .define import WireNetwork, WireAccessPoint
    DmPosData = tuple[int, tuple[int, int, int]]
# TYPE_CHECKING END


# TODO: 我的山头: 需要 GC
WireNetworkPool = {} # type: dict[DmPosData, tuple[set[WireNetwork], set[WireNetwork]]]
WireAccessPointPool = WValueDict() # type: WValueDict[tuple[int, int, int, int, int], WireAccessPoint] # (dim, x, y, z, access_facing)
GNodes = {} # type: dict[int, WValueDict[tuple[int, int, int], WireNetwork]]
