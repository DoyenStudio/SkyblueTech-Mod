# coding=utf-8
import base64
import json
from collections import Counter

from mod.server.extraServerApi import GetPlayerList
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.events.basic import ServerEvent
from skybluetech_scripts.tooldelta.events.server.world import DelServerPlayerEvent
from skybluetech_scripts.tooldelta.extensions.ui_sync import AddSyncPending
from ...common.define import id_enum
from ...common.utils import blueprint as bp
from ...common.events.machinery.blueprint import BlueprintAction, BlueprintUpdate
from .basic import GUIControl, ItemContainer, OperationListener
from .core import RegisterMachine
from .utils.blueprint_layout import Layout
from .utils.blueprint_inventory import refund, finish_destroyed_refund
from .utils.blueprint_tasks import capture, examine, build_batch

selecting = {}
watching = {}


class DimensionChangeFinishServerEvent(ServerEvent):
    name = "DimensionChangeFinishServerEvent"

    @classmethod
    def unmarshal(cls, data):
        event = cls()
        event.playerId = data["playerId"]
        event.fromDimensionId = data["fromDimensionId"]
        event.toDimensionId = data["toDimensionId"]
        event.toPos = data["toPos"]
        return event


class ServerChatEvent(ServerEvent):
    name = "ServerChatEvent"

    @classmethod
    def unmarshal(cls, data):
        event = cls()
        event.playerId = data["playerId"]
        event.message = data["message"]
        event.data = data
        return event

    def cancel(self):
        self.data["cancel"] = True


def reopen_container(player, screen, title):
    return CF.CreatePlayer(player).OpenNeteaseContainer(screen, title, True)


@RegisterMachine
class BlueprintTable(OperationListener, ItemContainer, GUIControl):
    block_name = id_enum.Machinery.BLUEPRINT_TABLE
    is_non_energy_machine = True

    def __init__(self, dim, x, y, z, block_entity_data):
        super(BlueprintTable, self).__init__(dim, x, y, z, block_entity_data)
        self.location = (dim, x, y, z)
        self.work = self.layout = self.saved_counts = None
        self.needs = Counter()
        self.status = ""
        self.reopen_on_error = None
        self.job = json.loads(self.bdata["bp_job"] or "null")
        self.task_owner = None
        self.waiting_ok = set()
        self.planned = None
        if self.job and not self.job["returning"]:
            self.planned = bytearray(base64.b64decode(self.bdata["bp_plan"]))
            try:
                self.layout = Layout(bp.unshare(self.job["code"]), self.xyz, self.job["facing"])
            except ValueError:
                self.job["returning"] = True
                self.status = "蓝图方块已不可用，退还剩余材料"
        self.handler.SubscribeOnTicking(self.tick)
        self.handler.SubscribeOnDestroy(self.destroy)
        self.handler.SubscribeOnUnload(self.unload)

    def facing(self):
        states = CF.CreateBlockState(LEVEL_ID).GetBlockStates(self.xyz, self.dim) or {}
        return bp.DIRECTIONS.index(states["minecraft:cardinal_direction"])

    def mode(self):
        return self.bdata["bp_mode"] or "save"

    def draft(self):
        return self.bdata["bp_input"] or ""

    def save_snapshot(self, blob):
        # Keep each individual block-entity string below the NBT string limit.
        encoded = base64.b64encode(blob)
        chunks = [encoded[i:i + 16000] for i in range(0, len(encoded), 16000)]
        previous = self.bdata["bp_chunks"] or 1
        self.bdata["bp_snapshot"] = chunks[0]
        for i in range(1, max(len(chunks), previous)):
            self.bdata["bp_snapshot_%d" % i] = chunks[i] if i < len(chunks) else ""
        self.bdata["bp_chunks"] = len(chunks)

    def snapshot_blob(self):
        chunks = [self.bdata["bp_snapshot"] or ""]
        for i in range(1, self.bdata["bp_chunks"] or 1):
            chunks.append(self.bdata["bp_snapshot_%d" % i])
        return base64.b64decode("".join(chunks))

    def IsValidInput(self, slot, item):
        return False

    def send(self, player, action, value=None):
        BlueprintUpdate(self.location, action, value).send(player)

    def notice(self, player, message):
        if player in GetPlayerList():
            CF.CreateMsg(LEVEL_ID).NotifyOneMessage(player, message)

    def reopen(self, player):
        if player in GetPlayerList() and watching.get(player) is self:
            self.send(player, "selected")
            AddSyncPending(player, self.ui_sync)
            reopen_container(player, "BlueprintTableUI.main", "蓝图工作台")

    def publish(self):
        saving = self.mode() == "save"
        counts = self.needs
        if saving:
            code = self.bdata["bp_output"] or ""
            if any(ch not in bp.BASE91_DIGITS for ch in bp.as_text(code)):
                code = ""
            if self.saved_counts is None:
                blob = self.snapshot_blob()
                self.saved_counts = (Layout(bp.unpack(blob), self.xyz,
                                            self.facing()).counts if blob else Counter())
            counts = self.saved_counts
        else:
            code = self.draft()
        payload = {
            "mode": self.mode(), "code": code,
            "rows": [(name, aux, n) for (name, aux), n in sorted(counts.items())],
            "locked": bool(self.job or self.task_owner),
            "status": self.status, "ready": not self.work and not self.job and
                (bool(self.bdata["bp_snapshot"]) if saving else bool(self.layout and self.needs)),
            "facing": self.facing(), "variants": self.layout.variants if self.layout and not saving and not self.job else [],
        }
        for player in tuple(self.ui_sync.GetPlayersInSync()):
            if watching.get(player) is self:
                self.send(player, "state", payload)

    def clear_previews(self):
        for player, machine in list(watching.items()):
            if machine is self:
                self.send(player, "clear")

    def refresh_build(self, player, start=False):
        self.needs.clear()
        self.layout = None
        self.work = None
        self.status = ""
        code = self.draft()
        if code:
            try:
                self.layout = Layout(bp.unshare(code), self.xyz, self.facing())
            except ValueError as error:
                self.status = "蓝图码校验失败"
                if ":" in str(error):
                    self.status += "：" + str(error)
            else:
                self.work = examine(self, player, start)
                self.task_owner = player if start else None
                self.status = "正在核对材料与位置"
        self.publish()

    def generate(self):
        blob = self.snapshot_blob()
        code = bp.share(blob) if 0 < len(blob) <= 500 else ""
        if not blob:
            self.status = "请先选择范围"
        elif not code or len(code) > 500:
            self.status = "信息量超限"
            code = ""
        else:
            self.status = ("蓝图码超过300字符（%d字符）" if len(code) > 300 else "已生成（%d字符）") % len(code)
        self.bdata["bp_output"] = code
        self.publish()

    def start_job(self, player, code, planned, escrow):
        self.planned = planned
        self.bdata["bp_plan"] = base64.b64encode(bytes(planned))
        self.job = {"code": code, "facing": self.facing(), "player": player, "escrow": escrow,
                    "index": 0, "returning": False}
        self.checkpoint()
        self.status = "正在搭建"
        self.clear_previews()

    def checkpoint(self):
        self.bdata["bp_job"] = json.dumps(self.job, separators=(",", ":"))

    def return_stacks(self, player, escrow):
        refund(escrow, player, self.dim, self.xyz)
        if escrow:
            self.job = {"returning": True, "player": player, "escrow": escrow}
            self.checkpoint()

    def finish_job(self):
        refund(self.job["escrow"], self.job["player"], self.dim, self.xyz)
        if not self.job["escrow"]:
            self.job = self.planned = None
            self.bdata["bp_plan"] = ""
            self.layout = None
            self.needs.clear()
        self.checkpoint()
        self.publish()

    def stop_job(self, reason):
        self.status = reason
        self.notice(self.job["player"], reason)
        self.job["returning"] = True
        self.checkpoint()
        self.finish_job()

    def tick(self):
        if self.job:
            build_batch(self)
        elif self.work:
            try:
                next(self.work)
                return
            except StopIteration:
                pass
            except ValueError as error:
                self.status = str(error)
                if self.reopen_on_error:
                    self.notice(self.reopen_on_error, self.status)
                    self.reopen(self.reopen_on_error)
            self.work = self.task_owner = self.reopen_on_error = None
            self.publish()

    def destroy(self):
        if self.job:
            job, self.job = self.job, None
            finish_destroyed_refund(job["escrow"], job["player"], self.dim, self.xyz)
            self.notice(job["player"], "工作台已拆除，退还剩余材料")

    def unload(self):
        for player, machine in list(watching.items()):
            if machine is self:
                self.send(player, "leave")
                watching.pop(player, None)
                selecting.pop(player, None)
        self.work = None

    def operate(self, player, action, value):
        if action == "target":
            if selecting.get(player) is not self or player not in self.waiting_ok:
                return
            self.waiting_ok.discard(player)
            if not isinstance(value, (tuple, list)) or len(value) != 3 or not all(type(v) is int for v in value):
                self.notice(player, "请瞄准方块后输入 OK")
                return
            _, size = bp.bounds(bp.front(self.xyz, self.facing()), value)
            if any(n > cap for n, cap in zip(size, bp.LIMIT)):
                self.notice(player, "超出范围")
                return
            if self.mode() != "save" or self.work or self.job:
                self.notice(player, "工作台正忙或模式已改变")
                return
            selecting.pop(player, None)
            self.reopen_on_error = self.task_owner = player
            self.work = capture(self, player, tuple(value))
            self.send(player, "capturing")
            return

        if not self.ui_sync.PlayerInSync(player):
            return
        if action == "open":
            previous = watching.get(player)
            if previous and previous is not self:
                previous.send(player, "leave")
            selecting.pop(player, None)
            watching[player] = self
            if self.mode() == "build" and not self.job and not self.work:
                self.refresh_build(player)
            else:
                self.publish()
            return
        if watching.get(player) is not self:
            return
        if self.job or self.task_owner:
            self.publish()
            return
        if action == "mode" and value in ("build", "save"):
            self.clear_previews()
            for other, machine in list(selecting.items()):
                if machine is self:
                    selecting.pop(other)
                    self.send(other, "leave")
            self.bdata["bp_mode"] = value
            self.work = None
            if value == "build":
                self.refresh_build(player)
            else:
                self.status = ""
                self.publish()
        elif self.mode() == "save" and action == "select":
            selecting[player] = self
            self.send(player, "select", self.facing())
        elif self.mode() == "save" and action == "confirm":
            self.generate()
        elif self.mode() == "build" and action == "edit":
            if not isinstance(value, (str, bp.py2_unicode)):
                return
            text = bp.as_text(value)
            self.bdata["bp_input"] = text[:501].encode("utf-8")
            self.clear_previews()
            self.refresh_build(player)
        elif self.mode() == "build" and action == "confirm" and value == self.draft() and not self.work:
            self.refresh_build(player, True)


@BlueprintTable.ForOperation(BlueprintAction)
def on_action(event, machine):
    machine.operate(event.player_id, event.action, event.value)


@ServerChatEvent.Listen()
def on_chat(event):
    machine = selecting.get(event.playerId)
    if machine is None or event.message.lower() != "ok":
        return
    if CF.CreateDimension(event.playerId).GetEntityDimensionId() != machine.dim:
        selecting.pop(event.playerId, None)
        return
    event.cancel()
    machine.waiting_ok.add(event.playerId)
    machine.send(event.playerId, "request_target")


@DelServerPlayerEvent.Listen()
def on_leave(event):
    leave_table(event.id)


@DimensionChangeFinishServerEvent.Listen()
def on_dimension_change(event):
    leave_table(event.playerId)


def leave_table(player):
    selecting.pop(player, None)
    machine = watching.pop(player, None)
    if machine:
        machine.waiting_ok.discard(player)
