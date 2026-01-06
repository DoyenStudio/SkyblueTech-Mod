# coding=utf-8
#
from weakref import WeakValueDictionary as WValueDict
from ....tooldelta.no_runtime_typing import TYPE_CHECKING

# TYPE_CHECKING
if TYPE_CHECKING:
    from .define import PipeNetwork, PipeAccessPoint
    DmPosData = tuple[int, tuple[int, int, int]]
# TYPE_CHECKING END

pool = WValueDict() # type: WValueDict[int, PipeNetwork]

def GetSameNetwork(network):
    # type: (PipeNetwork) -> PipeNetwork
    network_hash = hash(network)
    if network_hash in pool:
        return pool[network_hash]
    else:
        pool[network_hash] = network
        return network


# TODO: 我的山头: 需要 GC
tankNetworkPool = {} # type: dict[DmPosData, tuple[set[PipeNetwork], set[PipeNetwork]]]
tankAccessPointPool = WValueDict() # type: WValueDict[tuple[int, int, int, int, int], PipeAccessPoint] # (dim, x, y, z, access_facing)
