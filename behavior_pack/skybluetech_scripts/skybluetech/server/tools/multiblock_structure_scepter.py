# coding=utf-8
# 先扫描可放置位置, 再按背包材料分帧搭建, 最后重新检查并报告坐标。

from collections import deque

from mod.server.extraServerApi import GetMinecraftEnum, GetPlayerList
from mod_log import logger

from skybluetech_scripts.skybluetech.common.machinery_def.multi_block_structures import (
    CONTROLLER_STRUCTURE_PALETTES,
)
from skybluetech_scripts.skybluetech.common.utils.structure_build_plan import (
    create_build_plan,
)
from skybluetech_scripts.skybluetech.common.utils.structure_palette import AIR_BLOCK_ID
from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.events.server import DelServerPlayerEvent
from skybluetech_scripts.tooldelta.extensions.rate_limiter import PlayerRateLimiter
from skybluetech_scripts.tooldelta.general import ServerUninitCallback
from skybluetech_scripts.tooldelta.internal import GetServer
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.utils.timer import ExecLater

from ..machinery.basic.multi_block_structure import (
    MAX_STRUCTURE_MISMATCH_POSES,
    ROT_TIMES_MAPPING,
    detect_areas,
    mark_detect_area_dirty,
)
from ..machinery.core.registry import TryGetMachineCls
from ..machinery.utils.bans import is_machine_banned, reject_banned_machine

ItemPosType = GetMinecraftEnum().ItemPosType
PLACE_FACING = GetMinecraftEnum().Facing.Up
SCAN_PER_TICK = 32
BUILD_PER_TICK = 8
REPORT_LINES_PER_TICK = 1
limiter = PlayerRateLimiter(1)
player_jobs = {}  # type: dict[str, StructureBuildJob]
controller_jobs = {}  # type: dict[tuple[int, tuple[int, int, int]], StructureBuildJob]


def try_build(player_id, controller_id, dim, pos):
    # type: (str, str, int, tuple[int, int, int]) -> bool
    """供机器的两种点击事件入口调用; True 表示已处理, 应取消常规交互。"""

    palette = CONTROLLER_STRUCTURE_PALETTES.get(controller_id)
    if palette is None:
        return False
    if not limiter.record(player_id):
        return True
    if player_id in player_jobs or (dim, pos) in controller_jobs:
        CF.CreateGame(LEVEL_ID).SetOneTipMessage(
            player_id, "§e正在处理多方块结构，请稍候"
        )
        return True
    if reject_banned_machine(player_id, controller_id):
        return True
    states = CF.CreateBlockState(LEVEL_ID).GetBlockStates(pos, dim) or {}
    facing = states.get("minecraft:cardinal_direction")
    if facing not in ROT_TIMES_MAPPING:
        CF.CreateGame(LEVEL_ID).SetOneTipMessage(player_id, "§c无法读取控制器朝向")
        return True
    for _ in range(ROT_TIMES_MAPPING[facing]):
        palette = palette.rotate()
    job = StructureBuildJob(player_id, controller_id, dim, pos, facing, palette)
    player_jobs[player_id] = job
    controller_jobs[(dim, pos)] = job
    CF.CreateGame(LEVEL_ID).SetOneTipMessage(
        player_id, "§b正在检查多方块结构的可放置位置……"
    )
    ExecLater(0, job.tick)
    return True


class StructureBuildJob(object):
    def __init__(self, player_id, controller_id, dim, pos, facing, palette):
        self.player_id = player_id
        self.controller_id = controller_id
        self.dim = dim
        self.pos = pos
        self.facing = facing
        self.palette = palette
        self.placed_count = 0
        self.candidates = []
        self.original_blocks = {}
        self.required_left = palette.require_blocks_count.copy()
        self.item_names = {AIR_BLOCK_ID: "空气"}
        self.messages = deque()
        self.mismatch_count = 0
        self.missing_required = {}
        machine_cls = TryGetMachineCls(controller_id)
        self.functional_ids = (
            getattr(machine_cls, "functional_block_ids") if machine_cls else set()
        )
        self.expected = {}  # type: dict[tuple[int, int, int], tuple[str, ...]]
        cx, cy, cz = pos
        for index, poses in palette.posblock_data.items():
            block_ids = palette._to_block_ids(palette.palette_data[index])
            for x, y, z in poses:
                self.expected[(cx + x, cy + y, cz + z)] = block_ids
        for x, y, z in palette.air_poses:
            self.expected[(cx + x, cy + y, cz + z)] = (AIR_BLOCK_ID,)
        # 连同不参与图案匹配的格子一起复查, 以发现被藏在结构内的功能接口。
        self.positions = [
            (cx + x, cy + y, cz + z)
            for y in range(palette.min_y, palette.max_y + 1)
            for z in range(palette.min_z, palette.max_z + 1)
            for x in range(palette.min_x, palette.max_x + 1)
            if (x, y, z) != (0, 0, 0)
        ]
        self.pending = deque(self.positions)
        self.phase = self.scan

    def tick(self):
        if player_jobs.get(self.player_id) is not self:
            return
        if self.player_id not in GetPlayerList():
            self.release()
            return
        if CF.CreateDimension(self.player_id).GetEntityDimensionId() != self.dim:
            self.abort("玩家已切换维度")
            return
        comp = CF.CreateBlockInfo(LEVEL_ID)
        block = comp.GetBlockNew(self.pos, self.dim) or {}
        states = CF.CreateBlockState(LEVEL_ID).GetBlockStates(self.pos, self.dim) or {}
        if (
            block.get("name") != self.controller_id
            or states.get("minecraft:cardinal_direction") != self.facing
            or is_machine_banned(self.controller_id)
        ):
            self.abort("控制器已改变、卸载或被禁用")
            return
        self.phase()
        if player_jobs.get(self.player_id) is self:
            ExecLater(0, self.tick)

    def scan(self):
        comp = CF.CreateBlockInfo(LEVEL_ID)
        for _ in range(min(SCAN_PER_TICK, len(self.pending))):
            pos = self.pending.popleft()
            allowed = self.expected.get(pos)
            if not allowed or allowed == (AIR_BLOCK_ID,):
                continue
            block = comp.GetBlockNew(pos, self.dim)
            if block is None:
                continue
            actual = block.get("name")
            if actual in allowed:
                if actual in self.required_left:
                    self.required_left[actual] = max(0, self.required_left[actual] - 1)
                continue
            placeable = tuple(
                block_id
                for block_id in allowed
                if block_id != AIR_BLOCK_ID
                and not is_machine_banned(block_id)
                and comp.MayPlace(block_id, pos, PLACE_FACING, self.dim)
            )
            if placeable:
                self.candidates.append((pos, placeable))
                self.original_blocks[pos] = (actual, block.get("aux", 0))
        if self.pending:
            return
        counts = {}
        for raw in (
            CF.CreateItem(self.player_id).GetPlayerAllItems(ItemPosType.INVENTORY, True)
            or []
        ):
            if raw is None:
                continue
            item = Item.from_dict(raw)
            if item.newAuxValue == 0 and item.count > 0:
                counts[item.id] = counts.get(item.id, 0) + item.count
        self.pending = deque(
            create_build_plan(self.candidates, counts, self.required_left)
        )
        self.phase = self.build

    def build(self):
        comp = CF.CreateBlockInfo(LEVEL_ID)
        changed = []
        for _ in range(min(BUILD_PER_TICK, len(self.pending))):
            pos, block_id = self.pending.popleft()
            block = comp.GetBlockNew(pos, self.dim)
            # 跨帧期间已有玩家搭好或改过该位置时跳过, 不覆盖现有方块。
            if (
                block is None
                or block.get("name") in self.expected[pos]
                or (block.get("name"), block.get("aux", 0)) != self.original_blocks[pos]
                or is_machine_banned(block_id)
                or not comp.MayPlace(block_id, pos, PLACE_FACING, self.dim)
            ):
                continue
            if self.place_from_inventory(pos, block_id):
                changed.append(pos)
                self.placed_count += 1
        # SetBlockNew 不是玩家放置事件, 显式刷新所有受影响的结构, 包括相邻控制器。
        for area in tuple(detect_areas.get(self.dim, ())):
            if area.has_bound and any(area.is_inside(*pos) for pos in changed):
                mark_detect_area_dirty(area)
        if not self.pending:
            self.pending = deque(self.positions)
            self.required_left = self.palette.require_blocks_count.copy()
            self.phase = self.check_result

    def place_from_inventory(self, pos, block_id):
        # 扫描结束后才开始扣料。逐块读取真实槽位, 扣料与放置之间不跨帧;
        # 玩家在建造期间移动/使用了材料时, 只使用当前仍持有的那部分。
        item_comp = CF.CreateItem(self.player_id)
        for slot, raw in enumerate(
            item_comp.GetPlayerAllItems(ItemPosType.INVENTORY, True) or []
        ):
            if raw is None:
                continue
            item = Item.from_dict(raw)
            if item.id != block_id or item.newAuxValue != 0 or item.count <= 0:
                continue
            if not item_comp.SetInvItemNum(slot, item.count - 1):
                return False
            if CF.CreateBlockInfo(LEVEL_ID).SetBlockNew(
                pos,
                {"name": block_id, "aux": 0},
                0,
                self.dim,
            ):
                return True
            self.refund(slot, raw)
            return False
        return False

    def refund(self, slot, original):
        "放置失败时恢复原槽; 槽位被同步回调改动过则把这一份材料掉在控制器旁。"
        comp = CF.CreateItem(self.player_id)
        current = comp.GetPlayerItem(ItemPosType.INVENTORY, slot, True)
        previous = original.copy()
        previous["count"] -= 1
        if previous["count"] > 0:
            unchanged = current == previous
        else:
            unchanged = (
                not current
                or current.get("count", 0) == 0
                or current.get("newItemName") == AIR_BLOCK_ID
            )
        if unchanged:
            result = comp.SetPlayerAllItems({(ItemPosType.INVENTORY, slot): original})
            if result and result.get((ItemPosType.INVENTORY, slot)):
                return
        refund = original.copy()
        refund["count"] = 1
        x, y, z = self.pos
        if (
            GetServer().CreateEngineItemEntity(
                refund, self.dim, (x + 0.5, y + 1, z + 0.5)
            )
            is None
        ):
            logger.error(
                "SkyblueTech: scepter refund failed: %s, slot %d"
                % (self.player_id, slot)
            )
            CF.CreateMsg(LEVEL_ID).NotifyOneMessage(
                self.player_id,
                "§c材料返还失败：%s ×1，请联系管理员"
                % self.item_name(refund["newItemName"]),
            )

    def check_result(self):
        comp = CF.CreateBlockInfo(LEVEL_ID)
        for _ in range(min(SCAN_PER_TICK, len(self.pending))):
            pos = self.pending.popleft()
            block = comp.GetBlockNew(pos, self.dim)
            actual = block.get("name") if block else None
            allowed = self.expected.get(pos)
            if allowed:
                if actual in allowed:
                    if actual in self.required_left:
                        self.required_left[actual] = max(
                            0, self.required_left[actual] - 1
                        )
                else:
                    self.add_mismatch(pos, allowed, actual)
            elif actual in self.functional_ids:
                self.add_mismatch(pos, (AIR_BLOCK_ID,), actual)
        if self.pending:
            return
        self.missing_required = {
            block_id: count
            for block_id, count in self.required_left.items()
            if count > 0
        }
        for block_id, count in sorted(self.missing_required.items()):
            self.messages.append(
                "§7[§e!§7] 最低数量不足： §e还缺 %d 个 %s"
                % (count, self.item_name(block_id))
            )
        summary = "§b多方块建造完成： 已放置 %d 个方块" % self.placed_count
        if self.mismatch_count:
            summary += "；\n§7[§cx§7] §7还有 §c%d§7 处方块不匹配" % self.mismatch_count
            if self.mismatch_count > MAX_STRUCTURE_MISMATCH_POSES:
                summary += "（仅列出前 %d 处）" % MAX_STRUCTURE_MISMATCH_POSES
        if self.missing_required:
            summary += "；\n§7[§e!§7] 必需方块数量仍不足"
        if self.mismatch_count or self.missing_required:
            summary += "， 详情见聊天栏"
        else:
            summary += "；\n§7[§a!§7] §a结构已完成"
        CF.CreateGame(LEVEL_ID).SetOneTipMessage(self.player_id, summary)
        CF.CreateMsg(LEVEL_ID).NotifyOneMessage(self.player_id, summary)
        self.phase = self.report

    def item_name(self, item_id):
        # type: (str | None) -> str
        "返回本地化名称; 空气没有物品基础信息, 未知方块也不显示原始 ID。"
        if not item_id:
            return "未加载"
        if item_id not in self.item_names:
            info = CF.CreateItem(LEVEL_ID).GetItemBasicInfo(item_id, 0) or {}
            name = info.get("itemName") or "未知方块"
            self.item_names[item_id] = name.replace("§r", "").replace("§f", "")
        return self.item_names[item_id]

    def add_mismatch(self, pos, allowed, actual):
        self.mismatch_count += 1
        if self.mismatch_count > MAX_STRUCTURE_MISMATCH_POSES:
            return
        self.messages.append(
            "§e(%d, %d, %d) §7需要§f%s§7； 当前为§f%s"
            % (
                pos
                + (
                    " / ".join(self.item_name(item_id) for item_id in allowed),
                    self.item_name(actual),
                )
            )
        )

    def report(self):
        if not self.messages:
            self.release()
            return
        # 每条坐标单独发送, 避免多行拼接后超过聊天消息长度而丢失末尾内容。
        msg_comp = CF.CreateMsg(LEVEL_ID)
        for _ in range(min(REPORT_LINES_PER_TICK, len(self.messages))):
            msg_comp.NotifyOneMessage(self.player_id, self.messages.popleft())

    def abort(self, reason):
        CF.CreateMsg(LEVEL_ID).NotifyOneMessage(
            self.player_id,
            "§e多方块建造已停止：%s；已放置 %d 个方块" % (reason, self.placed_count),
        )
        self.release()

    def release(self):
        if player_jobs.get(self.player_id) is self:
            del player_jobs[self.player_id]
        if controller_jobs.get((self.dim, self.pos)) is self:
            del controller_jobs[(self.dim, self.pos)]


@DelServerPlayerEvent.Listen()
def on_player_leave(event):
    # type: (DelServerPlayerEvent) -> None
    job = player_jobs.get(event.id)
    if job is not None:
        job.release()


@ServerUninitCallback()
def on_server_uninit():
    player_jobs.clear()
    controller_jobs.clear()
