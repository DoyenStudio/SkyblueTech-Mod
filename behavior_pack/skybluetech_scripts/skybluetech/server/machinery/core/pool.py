# coding=utf-8
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
"机器实例的创建、查询、移除及缓存失效; 不注册游戏事件监听。"
from skybluetech_scripts.skybluetech.common.define.facing import (
    DXYZ_FACING,
    FACING_DXYZ,
)
from skybluetech_scripts.tooldelta.utils.timer import ExecLater

from .registry import TryGetMachineCls

# TYPE_CHECKING
if 0 > 1:
    import typing

    from ..basic.base_machine import BaseMachine
# TYPE_CHECKING END


cached_machines = {}  # type: dict[tuple[int, int, int, int], BaseMachine]

_invalidated_positions = set()  # type: set[tuple[int, int, int, int]]
"本 tick 内被请求失效的机器坐标, tick 末统一派发。"
_flush_scheduled = False
"是否已经排好一次派发, 避免同一 tick 内重复排队。"


def InvalidateMachineCachesLater(dim, positions):
    # type: (int, typing.Iterable[tuple[int, int, int]]) -> None
    """
    把一批坐标上机器的缓存失效请求排到本 tick 结束后统一派发。

    管网重建会在一次事件里连续拆建多条网络, 同一台机器可能被反复命中;
    合并成 tick 末一次派发, 既避免重复回调, 也避免机器代码在管网拆到
    一半时被同步唤起。
    """
    global _flush_scheduled
    _invalidated_positions.update((dim, x, y, z) for x, y, z in positions)
    if not _flush_scheduled:
        _flush_scheduled = True
        ExecLater(0, _flush_invalidated_machine_caches)


def _flush_invalidated_machine_caches():
    # type: () -> None
    "派发本 tick 内积攒的失效请求; 期间已被卸载的机器直接跳过。"
    global _flush_scheduled
    _flush_scheduled = False
    positions = list(_invalidated_positions)
    _invalidated_positions.clear()
    for pos in positions:
        m = cached_machines.get(pos)
        if m is not None:
            m.handler.CallOnInvalidateCachesHandlers()


def _get_machine(dimension, x, y, z, machine_cls):
    # type: (int, int, int, int, type[BaseMachine]) -> BaseMachine
    cache = cached_machines.get((dimension, x, y, z))
    if cache is not None:
        return cache
    return LoadMachine(dimension, x, y, z, machine_cls)


def GetNearbyMachines(
    dim,  # type: int
    x,  # type: int
    y,  # type: int
    z,  # type: int
    spec_facing=(),  # type: tuple[int, ...]
):
    if spec_facing:
        facings = {FACING_DXYZ[i]: i for i in spec_facing}
    else:
        facings = DXYZ_FACING
    for (dx, dy, dz), facing in facings.items():
        m = GetLoadedMachine(dim, x + dx, y + dy, z + dz)
        if m is not None:
            yield m, facing


def GetMachineWithoutCls(dimension, x, y, z, block_id=None):
    # type: (int, int, int, int, str | None) -> BaseMachine | None
    bname = block_id or (CF.CreateBlockInfo(LEVEL_ID).GetBlockNew(
        (x, y, z),
        dimension,
    ) or {}).get("name")
    if bname is None:
        return None
    block_cls = TryGetMachineCls(bname)
    if block_cls is None:
        return None
    return _get_machine(dimension, x, y, z, block_cls)


def GetLoadedMachine(dimension, x, y, z):
    # type: (int, int, int, int) -> BaseMachine | None
    return cached_machines.get((dimension, x, y, z))


def InvalidateNearbyCaches(dim, x, y, z):
    # type: (int, int, int, int) -> None
    "失效 (x,y,z) 周围 6 个邻居机器的缓存, 方块放置/移除/区块装卸/邻居变化时调用。"
    for dx, dy, dz in DXYZ_FACING:
        m = cached_machines.get((dim, x + dx, y + dy, z + dz))
        if m is not None:
            m.handler.CallOnInvalidateCachesHandlers()


def PopMachine(dimension, x, y, z, machine_cls):
    # type: (int, int, int, int, type[BaseMachine]) -> BaseMachine
    k = (dimension, x, y, z)
    if k in cached_machines:
        return cached_machines.pop(k)
    else:
        bdata = CF.CreateBlockEntityData(LEVEL_ID).GetBlockEntityData(dimension, (x, y, z))
        if bdata is None:
            raise RuntimeError("BlockEntityData load failed")
        return machine_cls(dimension, x, y, z, bdata)


def PopMachineStrict(dimension, x, y, z):
    # type: (int, int, int, int) -> BaseMachine | None
    return cached_machines.pop((dimension, x, y, z), None)


def LoadMachine(dimension, x, y, z, machine_cls):
    # type: (int, int, int, int, type[BaseMachine]) -> BaseMachine
    "从方块实体数据创建并登记实例; 区块加载时替换该位置的旧缓存。"
    bdata = CF.CreateBlockEntityData(LEVEL_ID).GetBlockEntityData(dimension, (x, y, z))
    if bdata is None:
        raise RuntimeError(
            "BlockEntityData load failed in %d ~ %d %d %d" % (dimension, x, y, z)
        )
    machine = machine_cls(dimension, x, y, z, bdata)
    cached_machines[(dimension, x, y, z)] = machine
    InvalidateNearbyCaches(dimension, x, y, z)
    return machine
