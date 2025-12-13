from skybluetech_scripts.tooldelta.events.server.world import ChunkAcquireDiscardedServerEvent, ChunkLoadedServerEvent
from skybluetech_scripts.tooldelta.api.server.block import GetBlockEntityData, GetBlockName
from skybluetech_scripts.tooldelta.no_runtime_typing import TYPE_CHECKING

# TYPE_CHECKING
if TYPE_CHECKING:
    from .basic.base_machine import BaseMachine
# TYPE_CHECKING END


machine_classes = {} # type: dict[str, type[BaseMachine]]
# 我们需要缓存机器数据以保证最大限度地减少 GetBlockEntityData 的调用
cached_machines = {} # type: dict[tuple[int, int, int, int], BaseMachine]

def GetMachine(dimension, x, y, z, machine_cls):
    # type: (int, int, int, int, type[BaseMachine]) -> BaseMachine
    cache = cached_machines.get((dimension, x, y, z))
    if cache is not None:
        return cache
    else:
        bdata = GetBlockEntityData(dimension, x, y, z)
        if bdata is None:
            raise RuntimeError("BlockEntityData load failed in %d ~ %d %d %d" % (dimension, x, y, z))
        cache = machine_cls(dimension, x, y, z, bdata)
        cached_machines[(dimension, x, y, z)] = cache
        return cache

def GetMachineWithoutCls(dimension, x, y, z, block_id=None):
    # type: (int, int, int, int, str | None) -> BaseMachine | None
    bname = block_id or GetBlockName(dimension, (x, y, z))
    if bname is None:
        return None
    block_cls = machine_classes.get(bname)
    if block_cls is None:
        return None
    return GetMachine(dimension, x, y, z, block_cls)

def GetMachineStrictCls(dimension, x, y, z, machine_cls, real_strict=False):
    # type: (int, int, int, int, type[BaseMachine], bool) -> BaseMachine | None
    if not real_strict:
        m = GetMachine(dimension, x, y, z, machine_cls)
    else:
        m = GetMachineStrict(dimension, x, y, z)
    if isinstance(m, machine_cls):
        return m
    else:
        return None

def GetMachineStrict(dimension, x, y, z):
    # type: (int, int, int, int) -> BaseMachine | None
    return cached_machines.get((dimension, x, y, z))

def PopMachine(dimension, x, y, z, machine_cls):
    # type: (int, int, int, int, type[BaseMachine]) -> BaseMachine
    k = (dimension, x, y, z)
    if k in cached_machines:
        return cached_machines.pop(k)
    else:
        bdata = GetBlockEntityData(dimension, x, y, z)
        if bdata is None:
            raise RuntimeError("BlockEntityData load failed")
        return machine_cls(dimension, x, y, z, bdata)

def PopMachineStrict(dimension, x, y, z):
    # type: (int, int, int, int) -> BaseMachine | None
    return cached_machines.pop((dimension, x, y, z), None)

def GetMachineCls(block_name):
    # type: (str) -> type[BaseMachine]
    return machine_classes[block_name]

@ChunkLoadedServerEvent.Listen()
def onChunkLoaded(event):
    # type: (ChunkLoadedServerEvent) -> None
    if not event.blockEntities:
        return
    for block_entity_posdata in event.blockEntities[:]:
        x = block_entity_posdata["posX"]
        y = block_entity_posdata["posY"]
        z = block_entity_posdata["posZ"]
        blockName = block_entity_posdata["blockName"]
        machine_cls = machine_classes.get(blockName)
        if machine_cls is None:
            continue
        bdata = GetBlockEntityData(event.dimension, x, y, z)
        if bdata is None:
            raise RuntimeError("BlockEntityData load failed in %d ~ %d %d %d" % (event.dimension, x, y, z))
        cached_machines[(event.dimension, x, y, z)] = machine_cls(event.dimension, x, y, z, bdata)

@ChunkAcquireDiscardedServerEvent.Listen()
def onChunkDiscarded(event):
    # type: (ChunkAcquireDiscardedServerEvent) -> None
    for block_entity_posdata in event.blockEntities:
        x = block_entity_posdata["posX"]
        y = block_entity_posdata["posY"]
        z = block_entity_posdata["posZ"]
        m = cached_machines.pop((event.dimension, x, y, z), None)
        if m is not None:
            m.Dump()
            m.OnUnload()
