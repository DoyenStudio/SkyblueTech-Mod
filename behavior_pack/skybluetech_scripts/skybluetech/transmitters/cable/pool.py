# coding=utf-8
#
from weakref import WeakValueDictionary as WValueDict
from ....tooldelta.no_runtime_typing import TYPE_CHECKING

# TYPE_CHECKING
if TYPE_CHECKING:
    from .define import CableNetwork
    DmPosData = tuple[int, tuple[int, int, int]]
# TYPE_CHECKING END

pool = WValueDict() # type: WValueDict[int, CableNetwork]

def GetSameNetwork(network):
    # type: (CableNetwork) -> CableNetwork
    network_hash = hash(network)
    if network_hash in pool:
        return pool[network_hash]
    else:
        pool[network_hash] = network
        return network


# TODO: 我的山头: 需要 GC
containerNetworkPool = {} # type: dict[DmPosData, tuple[set[CableNetwork], set[CableNetwork]]]

