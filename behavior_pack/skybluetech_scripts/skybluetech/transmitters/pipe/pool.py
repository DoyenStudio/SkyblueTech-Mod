# coding=utf-8
#
from weakref import WeakValueDictionary as WValueDict
from ....tooldelta.no_runtime_typing import TYPE_CHECKING

# TYPE_CHECKING
if TYPE_CHECKING:
    from .define import PipeNetwork, PipeAccessPoint
    DmPosData = tuple[int, tuple[int, int, int]]
# TYPE_CHECKING END


# TODO: 我的山头: 需要 GC
PipeNetworkPool = {} # type: dict[DmPosData, tuple[list[PipeNetwork], list[PipeNetwork]]]
PipeAccessPointPool = WValueDict() # type: WValueDict[tuple[int, int, int, int, int], PipeAccessPoint] # (dim, x, y, z, access_facing)
GNodes = {} # type: dict[int, WValueDict[tuple[int, int, int], PipeNetwork]]
