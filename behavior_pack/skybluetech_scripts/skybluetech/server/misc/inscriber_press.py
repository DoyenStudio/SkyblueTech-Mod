# coding=utf-8
import time
import uuid
from copy import deepcopy
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.events.server import (
    ServerItemTryUseEvent,
    DelServerPlayerEvent,
    PushUIRequest,
)
from skybluetech_scripts.tooldelta.extensions.player_inventory import (
    GetSelectedSlot,
    GetInventoryItem,
    SetInventoryItem,
)
from skybluetech_scripts.tooldelta.utils import nbt
from skybluetech_scripts.tooldelta.utils.timer import Repeat
from skybluetech_scripts.skybluetech.common.misc.inscriber_press import (
    EMPTY,
    STICK,
    GRID_KEY,
    IDENTITY_KEY,
    SCREEN,
    HOLD_SECONDS,
    STICK_GRID,
    ReadGrid,
)
from skybluetech_scripts.skybluetech.common.events.misc.inscriber_press import (
    PressAction,
    PressState,
)

sessions = {}  # type: dict[str, EditSession]


class EditSession(object):
    def __init__(self, slot, item, grid):
        self.token = uuid.uuid4().hex
        self.slot = slot
        self.identity = deepcopy(item.userData[IDENTITY_KEY])
        self.grid = grid
        self.hold = None  # type: tuple[int, int, float] | None
        self.serial = 0
        self.touched = time.time()


def close(player_id, message=""):
    session = sessions.pop(player_id, None)
    if session:
        PressState(session.token, closed=True, message=message).send(player_id)


def source_item(player_id, session):
    if GetSelectedSlot(player_id) != session.slot:
        return None
    item = GetInventoryItem(player_id, session.slot)
    if (
        item is None
        or item.id != EMPTY
        or item.count != 1
        or (item.userData or {}).get(IDENTITY_KEY) != session.identity
        or ReadGrid(item.userData) != session.grid
    ):
        return None
    return item


@ServerItemTryUseEvent.Listen()
def on_use(event):
    if event.item.id != EMPTY:
        return
    event.cancel()
    player = event.playerId
    if player in sessions:
        if source_item(player, sessions[player]) is not None:
            return
        close(player)
    slot = GetSelectedSlot(player)
    if slot < 0:
        return
    item = GetInventoryItem(player, slot)
    if item is None or item.id != EMPTY:
        return
    if item.count != 1:
        PressState("", closed=True, message="请先将空模板拆分为单个物品").send(player)
        return
    grid = ReadGrid(item.userData)
    if grid is None:
        PressState("", closed=True, message="模板雕刻数据异常，未修改物品").send(player)
        return
    item.userData = deepcopy(item.userData or {})
    item.userData[IDENTITY_KEY] = nbt.String(uuid.uuid4().hex)
    if not SetInventoryItem(player, slot, item):
        PressState("", closed=True, message="无法保存模板，请重新尝试").send(player)
        return
    session = EditSession(slot, item, grid)
    sessions[player] = session
    PushUIRequest(SCREEN, params={"session": session.token, "grid": grid}).send(player)


@PressAction.Listen()
def on_action(event):
    # type: (PressAction) -> None
    session = sessions.get(event.player_id)
    if session is None or event.session != session.token:
        return
    player = event.player_id
    session.touched = time.time()
    if event.action == "close":
        close(player)
        return
    item = source_item(player, session)
    if item is None:
        close(player, "来源模板已改变，雕刻已结束")
        return
    if event.action == "ping":
        return
    if type(event.serial) is not int:
        return
    if event.action == "cancel":
        if session.hold and session.hold[1] == event.serial:
            session.hold = None
        return
    index = event.index
    if type(index) is not int or not 0 <= index < 64 or not session.grid[index]:
        return
    if event.action == "start":
        if event.serial <= session.serial:
            return
        session.serial = event.serial
        session.hold = (index, event.serial, time.time())
        PressState(session.token, started=event.serial).send(player)
        return
    if event.action != "finish" or session.hold is None:
        return
    held_index, serial, started = session.hold
    if (index, event.serial) != (held_index, serial):
        return
    session.hold = None
    if time.time() - started < HOLD_SECONDS:
        PressState(session.token, session.grid).send(player)
        return
    grid = list(session.grid)
    grid[index] = 0
    completed = grid == STICK_GRID
    if completed:
        result = Item(STICK)
    else:
        result = item
        result.userData = deepcopy(item.userData or {})
        result.userData[GRID_KEY] = [nbt.Int(value) for value in grid]
    if not SetInventoryItem(player, session.slot, result):
        close(player, "模板保存失败，请重新打开")
        return
    session.grid = grid
    if completed:
        close(player)
    else:
        PressState(session.token, grid).send(player)


@DelServerPlayerEvent.Listen()
def on_leave(event):
    sessions.pop(event.id, None)


@Repeat(0.1)
def check_sessions():
    for player, session in list(sessions.items()):
        if time.time() - session.touched > 15 or source_item(player, session) is None:
            close(player)


check_sessions()
