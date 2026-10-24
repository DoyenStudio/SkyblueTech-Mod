# coding=utf-8
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
from mod.server.extraServerApi import GetMinecraftEnum

from skybluetech_scripts.tooldelta.utils.timer import ExecLater
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.events.server import (
    PushUIRequest,
    ServerItemTryUseEvent,
    ServerItemUseOnEvent,
)
from skybluetech_scripts.tooldelta.extensions.rate_limiter import PlayerRateLimiter
from skybluetech_scripts.tooldelta.utils import nbt
from skybluetech_scripts.tooldelta.utils.py_comp import py2_unicode
from skybluetech_scripts.skybluetech.common.define.id_enum import ObjectUpgraders
from skybluetech_scripts.skybluetech.common.events.misc.object_upgraders import (
    ObjUpVeinMinerSettingsAddBlockRequest,
    ObjUpVeinMinerSettingsUpload,
)

K_UD_VEIN_BLOCKS = "st:vein_blocks"
K_UI_VEIN_BLOCKS = "vein_blocks"
MAX_VEIN_BLOCKS = 256

limiter = PlayerRateLimiter(0.5)
STRING_TYPES = (str, py2_unicode)
add_block_pending = {}  # type: dict[str, int]
add_block_token_seq = 0


def _unpack_vein_blocks(ud):
    # type: (dict) -> list[str]
    raw = nbt.NBT2Py(ud.get(K_UD_VEIN_BLOCKS, []))
    if not isinstance(raw, list):
        return []
    return [str(i) for i in raw if isinstance(i, STRING_TYPES)]


def _is_valid_upload_blocks(new_blocks):
    # type: (object) -> bool
    if not isinstance(new_blocks, list):
        return False
    if len(new_blocks) > MAX_VEIN_BLOCKS:
        return False
    if not all(isinstance(i, STRING_TYPES) for i in new_blocks):
        return False
    return True


def _set_vein_blocks(player_id, item, vein_blocks):
    # type: (str, Item, list[str]) -> None
    ud = item.userData or {}
    ud[K_UD_VEIN_BLOCKS] = nbt.Py2NBT(vein_blocks)
    item.userData = ud
    CF.CreateItem(player_id).SpawnItemToPlayerCarried(item.marshal(), player_id)


def _on_add_block_timeout(player_id, token):
    # type: (str, int) -> None
    if add_block_pending.get(player_id) != token:
        return
    add_block_pending.pop(player_id, None)
    CF.CreateGame(LEVEL_ID).SetOnePopupNotice(player_id, "§c已超时", "§7[§6!§7] §6连锁采掘")


def _start_add_block(player_id):
    # type: (str) -> None
    global add_block_token_seq
    mainhand_item = CF.CreateItem(player_id).GetPlayerItem(
        GetMinecraftEnum().ItemPosType.CARRIED,
        0,
        True,
    )
    mainhand_item = Item.from_dict(mainhand_item) if mainhand_item is not None else None
    if mainhand_item is None or mainhand_item.id != ObjectUpgraders.VEINMINER:
        return
    ud = mainhand_item.userData or {}
    if len(_unpack_vein_blocks(ud)) >= MAX_VEIN_BLOCKS:
        CF.CreateGame(LEVEL_ID).SetOnePopupNotice(
            player_id,
            "§c最多只能添加 256 个可连锁采掘方块",
            "§7[§6!§7] §6连锁采掘",
        )
        return
    add_block_token_seq += 1
    token = add_block_token_seq
    add_block_pending[player_id] = token
    CF.CreateGame(LEVEL_ID).SetOnePopupNotice(
        player_id,
        "§e请在 10 秒内点击需要连锁采掘的方块",
        "§7[§6!§7] §6连锁采掘",
    )
    ExecLater(10, _on_add_block_timeout, player_id, token)


def _try_add_clicked_block(event):
    # type: (ServerItemUseOnEvent) -> bool
    player_id = event.entityId
    if player_id not in add_block_pending:
        return False
    add_block_pending.pop(player_id, None)
    mainhand_item = CF.CreateItem(player_id).GetPlayerItem(
        GetMinecraftEnum().ItemPosType.CARRIED,
        0,
        True,
    )
    mainhand_item = Item.from_dict(mainhand_item) if mainhand_item is not None else None
    if mainhand_item is None or mainhand_item.id != ObjectUpgraders.VEINMINER:
        CF.CreateGame(LEVEL_ID).SetOnePopupNotice(
            player_id,
            "§c添加失败：请手持连锁采掘升级选择方块",
            "§7[§6!§7] §6连锁采掘",
        )
        return True
    ud = mainhand_item.userData or {}
    vein_blocks = _unpack_vein_blocks(ud)
    block_id = str(event.blockName)
    if block_id in vein_blocks:
        CF.CreateGame(LEVEL_ID).SetOnePopupNotice(player_id, "§e该方块已在连锁采掘列表中", "§7[§6!§7] §6连锁采掘")
        return True
    if len(vein_blocks) >= MAX_VEIN_BLOCKS:
        CF.CreateGame(LEVEL_ID).SetOnePopupNotice(
            player_id,
            "§c最多只能添加 256 个可连锁采掘方块",
            "§7[§6!§7] §6连锁采掘",
        )
        return True
    vein_blocks.append(block_id)
    _set_vein_blocks(player_id, mainhand_item, vein_blocks)
    CF.CreateGame(LEVEL_ID).SetOnePopupNotice(
        player_id,
        "§a已添加： §f" + Item(block_id).GetBasicInfo().itemName,
        "§7[§a√§7] §a连锁采掘",
    )
    return True


def _try_open_settings_ui(player_id, item):
    # type: (str, Item) -> bool
    if (
        item.id != ObjectUpgraders.VEINMINER
        or not CF.CreatePlayer(player_id).isSneaking()
        or not limiter.record(player_id)
    ):
        return False
    ud = item.userData or {}
    vein_blocks = _unpack_vein_blocks(ud)
    PushUIRequest(
        "ObjUpVeinMinerSettingsUI.main",
        params={K_UI_VEIN_BLOCKS: vein_blocks},
    ).send(player_id)
    return True


@ServerItemTryUseEvent.ListenWithUserData()
def on_item_try_use(event):
    # type: (ServerItemTryUseEvent) -> None
    if _try_open_settings_ui(event.playerId, event.item):
        event.cancel()


@ServerItemUseOnEvent.ListenWithUserData()
def on_item_use_on(event):
    # type: (ServerItemUseOnEvent) -> None
    if _try_add_clicked_block(event):
        event.cancel()
        return
    if _try_open_settings_ui(event.entityId, event.item):
        event.cancel()


@ObjUpVeinMinerSettingsUpload.Listen()
def on_settings_upload(event):
    # type: (ObjUpVeinMinerSettingsUpload) -> None
    mainhand_item = CF.CreateItem(event.player_id).GetPlayerItem(
        GetMinecraftEnum().ItemPosType.CARRIED,
        0,
        True,
    )
    mainhand_item = Item.from_dict(mainhand_item) if mainhand_item is not None else None
    if mainhand_item is None or mainhand_item.id != ObjectUpgraders.VEINMINER:
        return
    new_blocks = event.vein_blocks
    if not _is_valid_upload_blocks(new_blocks):
        print("[Warning] ObjUpVeinMinerSettingsUpload: recv invalid vein_blocks")
        return
    _set_vein_blocks(event.player_id, mainhand_item, [str(i) for i in new_blocks])


@ObjUpVeinMinerSettingsAddBlockRequest.Listen()
def on_add_block_request(event):
    # type: (ObjUpVeinMinerSettingsAddBlockRequest) -> None
    _start_add_block(event.player_id)
