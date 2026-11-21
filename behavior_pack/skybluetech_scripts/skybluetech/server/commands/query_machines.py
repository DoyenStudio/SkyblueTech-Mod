# coding=utf-8
from collections import Counter

from mod.server.extraServerApi import GetPlayerList
from skybluetech_scripts.tooldelta.events.server import CustomCommandTriggerServerEvent
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.utils.timer import ExecLater
from ..machinery.core.pool import cached_machines
from .register import RegisterCommand
from .utils import generate_simple_arg_mapping


MAX_PAGE_LINES = 5
MAX_PAGE_BYTES = 128  # 只计明细，给机器总数留出空间。


def _make_pages(lines):
    pages = []
    page = []
    size = 0
    for line in lines:
        line_size = len(line if isinstance(line, bytes) else line.encode("utf-8"))
        if page and (len(page) >= MAX_PAGE_LINES or size + 1 + line_size > MAX_PAGE_BYTES):
            pages.append("\n".join(page))
            page = []
            size = 0
        size += line_size + bool(page)
        page.append(line)
    if page:
        pages.append("\n".join(page))
    return pages


def _send_page(player_id, pages, index):
    if player_id not in GetPlayerList():
        return
    CF.CreateMsg(LEVEL_ID).NotifyOneMessage(player_id, pages[index])
    if index + 1 < len(pages):
        ExecLater(0.2, _send_page, player_id, pages, index + 1)


@RegisterCommand("skybluetech:query_machines")
def query_machines(event):
    # type: (CustomCommandTriggerServerEvent) -> None
    if not cached_machines:
        event.SetReturnMsg("commands.skybluetech.query_machines.empty")
        return

    block_info = CF.CreateBlockInfo(LEVEL_ID)
    counts = Counter()
    for machine in cached_machines.values():
        block_id = machine.block_name
        if not block_id:
            # 多方块接口共用机器类，具体类型由所在位置的方块决定。
            block = block_info.GetBlockNew(machine.xyz, machine.dim) or {}
            block_id = block.get("name")
        counts[block_id] += 1

    item_comp = CF.CreateItem(LEVEL_ID)
    names = Counter()
    for block_id, count in counts.items():
        info = item_comp.GetItemBasicInfo(block_id, 0) if block_id else None
        name = (info or {}).get("itemName") or block_id or "未知机器"
        names[name] += count

    lines = [
        "%s：%d" % (name, count)
        for name, count in sorted(names.items(), key=lambda pair: (-pair[1], pair[0]))
    ]
    pages = _make_pages(lines)
    requested_page = generate_simple_arg_mapping(event.args).get("page")
    page = 1 if requested_page is None else requested_page
    if not 1 <= page <= len(pages):
        event.SetReturnMsg("commands.skybluetech.query_machines.invalid_page")
        event.SetReturnParams(str(len(pages)))
        event.SetReturnFailed()
        return

    event.SetReturnMsg("commands.skybluetech.query_machines.success")
    event.SetReturnParams(str(sum(counts.values())), pages[page - 1])
    player_id = event.origin.get("entityId")
    if requested_page is None and len(pages) > 1 and player_id in GetPlayerList():
        ExecLater(0.2, _send_page, player_id, pages, 1)
