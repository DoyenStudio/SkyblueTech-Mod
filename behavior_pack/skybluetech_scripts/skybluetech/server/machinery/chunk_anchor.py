# coding=utf-8
import time

from skybluetech_scripts.tooldelta.events.server import (
    ChunkAcquireDiscardedServerEvent,
    ChunkLoadedServerEvent,
)
from skybluetech_scripts.tooldelta.general import (
    ServerInitCallback,
    ServerUninitCallback,
)
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.utils.py_comp import py2_xrange
from ...common.events.machinery.chunk_anchor import ChunkAnchorRadiusRequest
from ...common.machinery_def.chunk_anchor import (
    ANCHOR,
    PORT,
    BEAM,
    BEAM_BLUE,
    BEAM_OFF,
    BEAM_RED,
    CAPACITY,
    RADIUS,
    STATUS,
    STRUCTURE_PALETTE,
    chunk_bounds,
    chunk_count,
)
from .basic import (
    GUIControl,
    MultiBlockStructure,
    MultiblockPortBindings,
    OperationListener,
)
from .core import RegisterMachine, pool
from .interfaces import EnergyInputInterface

EnergyInputInterface.AddExtraMachineId(PORT)
REGISTRY = "skybluetech:chunk_anchors"
DIMENSIONS = {0: "overworld", 1: "nether", 2: "the_end"}
SCRIPT_TICKS_PER_SECOND = 30.0
WAKE_TIMEOUT = 200 / SCRIPT_TICKS_PER_SECOND
RETRY_SECONDS = 10
records = None
anchors_by_chunk = {}
pending_checks = {}  # key -> (到期时间, 引擎定时器)
wake_deadlines = {}


def recorded_bounds(record):
    _, x, _, z = record["pos"]
    radius = record["area"]
    if radius < 0:
        return chunk_bounds(0, x, z)
    if "bounds" in record:
        return tuple(record["bounds"])
    # 旧存档中的常加载区按控制器和半径生成，可能未覆盖整个底座。
    cx, cz = x // 16, z // 16
    return cx - radius, cz - radius, cx + radius, cz + radius


def index_record(key, record, add):
    dim = record["pos"][0]
    min_x, min_z, max_x, max_z = recorded_bounds(record)
    for chunk_x in py2_xrange(min_x, max_x + 1):
        for chunk_z in py2_xrange(min_z, max_z + 1):
            chunk = (dim, chunk_x, chunk_z)
            if add:
                anchors_by_chunk.setdefault(chunk, set()).add(key)
            else:
                keys = anchors_by_chunk[chunk]
                keys.remove(key)
                if not keys:
                    del anchors_by_chunk[chunk]


def registry():
    global records
    if records is None:
        records = CF.CreateExtraData(LEVEL_ID).GetExtraData(REGISTRY) or {}
        for key, record in records.items():
            index_record(key, record, add=True)
    return records


def save():
    CF.CreateExtraData(LEVEL_ID).SetExtraData(REGISTRY, registry(), True)


def set_area(key, record, radius, bounds=None):
    index_record(key, record, add=False)
    record["area"] = radius
    if bounds is None:
        record.pop("bounds", None)
    else:
        record["bounds"] = list(bounds)
    index_record(key, record, add=True)
    wake_deadlines.pop(key, None)
    save()


def remove_record(key, record):
    was_removed = record["removed"]
    record["removed"] = True
    if not release(key, record):
        if not was_removed:
            save()
        schedule_check(key, RETRY_SECONDS)
        return
    index_record(key, record, add=False)
    del records[key]
    pending = pending_checks.pop(key, None)
    if pending is not None:
        CF.CreateGame(LEVEL_ID).CancelTimer(pending[1])
    wake_deadlines.pop(key, None)
    save()


def command(dim, tail):
    return CF.CreateCommand(LEVEL_ID).SetCommand(
        "/execute in %s run %s" % (DIMENSIONS[dim], tail), None, False
    )


def create_area(key, record, bounds):
    dim, _, y, _ = record["pos"]
    min_x, min_z, max_x, max_z = bounds
    return command(
        dim,
        "tickingarea add %d %d %d %d %d %d %s true"
        % (min_x * 16, y, min_z * 16, max_x * 16 + 15, y, max_z * 16 + 15, key),
    )


def release(key, record):
    if record["area"] < 0:
        return True
    dim = record["pos"][0]
    if dim not in DIMENSIONS:
        return False
    if not command(dim, "tickingarea remove " + key):
        # A failed query alone cannot distinguish absence from a disabled executor.
        if not command(dim, "testfor @a") or command(dim, "tickingarea preload " + key):
            return False
    set_area(key, record, -1)
    return True


@RegisterMachine
class ChunkAnchor(
    MultiblockPortBindings, OperationListener, GUIControl, MultiBlockStructure
):
    block_name = ANCHOR
    store_rf_max = CAPACITY
    energy_io_mode = (2,) * 6
    structure_palette = STRUCTURE_PALETTE
    functional_block_ids = {PORT}

    def __init__(self, dim, x, y, z, block_entity_data):
        super(ChunkAnchor, self).__init__(dim, x, y, z, block_entity_data)
        pos = [dim, x, y, z]
        self.key = "st_anchor_%d_%d_%d_%d" % tuple(pos)
        self.record = registry().get(self.key)
        if self.record is None:
            self.record = {"pos": pos, "area": -1, "removed": False}
            records[self.key] = self.record
            index_record(self.key, self.record, add=True)
            save()
        elif self.record["removed"]:
            self.record["removed"] = False
            save()
        wake_deadlines.pop(self.key, None)
        radius = self.bdata[RADIUS]
        self.radius = radius if type(radius) is int and -1 <= radius <= 4 else -1
        self.waited = 0
        self.retry_at = 0
        self.bdata[BEAM] = BEAM_OFF
        self.beam = BEAM_OFF
        self.last_message = None
        self.structure_checked = False
        self.handler.SubscribeOnTicking(self.tick)
        self.handler.SubscribeOnDestroy(self.destroy)
        self.handler.SubscribeOnUnload(self._on_unload)
        self.handler.SubscribeOnStructureChanged(self.structure_changed)

    def UnsetStructureDestroyed(self):
        already_formed = self.StructureFinished()
        MultiBlockStructure.UnsetStructureDestroyed(self)
        if already_formed:
            ports = self.GetAllMachines(EnergyInputInterface, PORT)
            if set(ports) != set(self._bound_ports):
                self._on_unload()
                self._bind_ports(ports)

    def _on_unload(self):
        self._unbind_ports(only_owned=True)

    def structure_changed(self, ok):
        if not ok:
            self.set_beam(BEAM_OFF)
        self.structure_checked = True
        self._on_unload()
        if ok:
            self._bind_ports(self.GetAllMachines(EnergyInputInterface, PORT))
        self.retry_at = 0

    def set_beam(self, beam):
        if self.beam != beam:
            self.beam = beam
            self.bdata[BEAM] = beam

    def status(self, message, beam=BEAM_OFF):
        self.set_beam(
            beam if self.StructureFinished() and self.radius >= 0 else BEAM_OFF
        )
        if self.last_message != message:
            self.last_message = message
            self.bdata[STATUS] = message
            self.CallSync()

    def stop(self, message, delay=0, beam=BEAM_OFF):
        if not release(self.key, self.record):
            beam = BEAM_RED
            message = "常加载区释放失败，正在重试"
            delay = 100
            self.cleanup_pending = True
        else:
            self.cleanup_pending = False
        self.waited = 0
        self.retry_at = time.time() + delay / SCRIPT_TICKS_PER_SECOND if delay else 0
        self.status(message, beam)

    cleanup_pending = False

    def destroy(self):
        self._on_unload()
        remove_record(self.key, self.record)

    def adjust(self, step):
        radius = max(-1, min(4, self.radius + step))
        if radius != self.radius:
            self.radius = radius
            self.bdata[RADIUS] = radius
            if radius < 0:
                self.stop("已关闭")
            else:
                self.retry_at = 0
                self.status("正在调整范围")

    def ensure_area(self, bounds):
        has_area = self.record["area"] >= 0
        exists = command(self.dim, "tickingarea preload " + self.key)
        if exists:
            if not has_area:
                self.stop("常加载区名称冲突", 100, BEAM_RED)
                return False
            if self.record["area"] == self.radius and recorded_bounds(self.record) == bounds:
                return True
            # 引擎在之后的 tick 才回收区域名称。保留记录，以便核心在此期间卸载后恢复。
            if command(self.dim, "tickingarea remove " + self.key):
                self.retry_at = time.time() + 2 / SCRIPT_TICKS_PER_SECOND
                self.status("正在重建常加载区")
            else:
                self.retry_at = time.time() + 100 / SCRIPT_TICKS_PER_SECOND
                self.status("常加载区释放失败，正在重试", BEAM_RED)
            schedule_check(self.key)
            return False
        if not create_area(self.key, self.record, bounds):
            if not command(self.dim, "testfor @a"):
                reason = "维度指令不可执行或没有执行者"
            elif sum(rec["area"] >= 0 for rec in registry().values()) - int(has_area) >= 10:
                reason = "世界常加载区名额已满"
            else:
                reason = "引擎拒绝创建，请检查名额和指令权限"
            self.retry_at = time.time() + 100 / SCRIPT_TICKS_PER_SECOND
            self.status(reason, BEAM_RED)
            if has_area:
                schedule_check(self.key)
            return False
        set_area(self.key, self.record, self.radius, bounds)
        self.waited = 0
        return True

    def tick(self):
        if self.retry_at:
            if time.time() < self.retry_at:
                return
            self.retry_at = 0
        if self.cleanup_pending:
            self.stop("正在重新检查")
            return
        structure_ready = self.StructureFinished()
        waiting_for_base = bool(self.area.chunks_not_loaded)
        # 已记录的常加载区可以先恢复底座，等区块就绪后再复核结构。
        restoring_area = (
            waiting_for_base and self.radius >= 0 and self.record["area"] == self.radius
        )
        if not self.structure_checked and not restoring_area and self.waited < 100:
            self.waited += 1
            self.status("正在核验底座")
            return
        if not structure_ready and not restoring_area:
            if waiting_for_base:
                reason = "底座跨区块，等待底座加载"
            elif PORT in self.GetStructureLackedBlocks():
                reason = "缺少能量输入口"
            else:
                reason = "底座不完整"
            self.stop(reason, 20)
            return
        if self.radius < 0:
            self.stop("已关闭")
            return
        bounds = chunk_bounds(self.radius, self.x, self.z)
        cost = 50 * chunk_count(bounds)
        if self.store_rf < cost:
            self.stop("电量不足", beam=BEAM_RED)
            return
        if self.dim not in DIMENSIONS:
            self.stop("当前维度不支持常加载", 100, BEAM_RED)
            return

        if not self.ensure_area(bounds):
            return
        min_x, min_z, max_x, max_z = bounds
        chunks = CF.CreateChunkSource(LEVEL_ID)
        if not structure_ready or not all(
            chunks.CheckChunkState(self.dim, (x * 16, self.y, z * 16))
            for x in py2_xrange(min_x, max_x + 1)
            for z in py2_xrange(min_z, max_z + 1)
        ):
            self.waited += 1
            if self.waited >= 100:
                self.stop("区块加载超时", 100, BEAM_RED)
            else:
                self.status("等待区块就绪")
            return
        self.waited = 0
        self.ReducePower(cost)
        self.status("运行中", BEAM_BLUE)


@ChunkAnchor.ForOperation(ChunkAnchorRadiusRequest, require_structure=False)
def change_radius(event, machine):
    if type(event.step) is not int or event.step not in (-1, 1):
        return
    if not machine.ui_sync.PlayerInSync(event.player_id):
        return
    pos = CF.CreatePos(event.player_id).GetFootPos()
    if pos and sum((a - b - 0.5) ** 2 for a, b in zip(pos, machine.xyz)) <= 64:
        machine.adjust(event.step)


def schedule_check(key, delay=1):
    due = time.time() + delay
    pending = pending_checks.get(key)
    # 同一台锚保留最早一次检查；新的区块事件可以提前触发较晚的重试。
    if pending is not None and pending[0] <= due:
        return
    game = CF.CreateGame(LEVEL_ID)
    if pending is not None:
        game.CancelTimer(pending[1])
    pending_checks[key] = due, game.AddTimer(delay, reconcile, key)


def check_unloaded_anchor(key, record):
    dim, x, _, z = record["pos"]
    radius = record["area"]
    if radius < 0 or dim not in DIMENSIONS:
        return
    deadline = wake_deadlines.get(key)
    if deadline is None:
        # 读档后常加载区可能先于控制器恢复，即使没有后续事件也要复查。
        deadline = time.time() + WAKE_TIMEOUT
        wake_deadlines[key] = deadline
    remaining = deadline - time.time()
    if remaining > 0:
        if not command(dim, "tickingarea preload " + key):
            bounds = chunk_bounds(radius, x, z)
            if create_area(key, record, bounds):
                set_area(key, record, radius, bounds)
                wake_deadlines[key] = deadline
        schedule_check(key, min(1, remaining))
    elif not release(key, record):
        schedule_check(key, RETRY_SECONDS)


def reconcile(key):
    pending_checks.pop(key, None)
    record = records.get(key)
    if record is None:
        return
    if record["removed"]:
        remove_record(key, record)
        return
    dim, x, y, z = record["pos"]
    machine = pool.GetLoadedMachine(dim, x, y, z)
    if machine is not None and machine.block_name == ANCHOR:
        wake_deadlines.pop(key, None)
        return
    pos = (x, y, z)
    if not CF.CreateChunkSource(LEVEL_ID).CheckChunkState(dim, pos):
        check_unloaded_anchor(key, record)
        return
    wake_deadlines.pop(key, None)
    block = CF.CreateBlockInfo(LEVEL_ID).GetBlockNew(pos, dim)
    if block:
        if block["name"] != ANCHOR:
            remove_record(key, record)
            return
        if CF.CreateBlockEntityData(LEVEL_ID).GetBlockEntityData(dim, pos) is not None:
            pool.GetMachineWithoutCls(dim, x, y, z, ANCHOR)
            return
    # 区块就绪时方块数据仍可能读不到，保留记录并单独重试。
    schedule_check(key, RETRY_SECONDS)


@ChunkLoadedServerEvent.Listen()
def mark_chunk_anchors_dirty(event):
    chunk = (event.dimension, event.chunkPosX, event.chunkPosZ)
    for key in anchors_by_chunk.get(chunk, ()):
        schedule_check(key)


@ChunkAcquireDiscardedServerEvent.Listen()
def on_anchor_chunk_discarded(event):
    mark_chunk_anchors_dirty(event)


@ServerInitCallback()
def restore_chunk_anchors():
    for key in registry():
        schedule_check(key)


@ServerUninitCallback()
def clear_registry_cache():
    global records
    game = CF.CreateGame(LEVEL_ID)
    for _, timer in pending_checks.values():
        game.CancelTimer(timer)
    pending_checks.clear()
    anchors_by_chunk.clear()
    wake_deadlines.clear()
    records = None
