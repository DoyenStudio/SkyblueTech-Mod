# coding=utf-8
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
from mod.server.extraServerApi import GetMinecraftEnum
from skybluetech_scripts.tooldelta.define import Item, BlockBasicInfo

from skybluetech_scripts.tooldelta.events.server import DestroyBlockEvent
from skybluetech_scripts.tooldelta.utils.timer import Delay
from ...common.tools_def.mining_hammer import MINING_HAMMERS

DIGGING_LEVEL_MAPPING = {
    "minecraft:stone_tier_destructible": 1,
    "minecraft:iron_tier_destructible": 2,
    "minecraft:diamond_tier_destructible": 3,
}
GameType = GetMinecraftEnum().GameType

player_digging_poses = {}  # type: dict[str, set[tuple[int, int, int]]]
_block_basic_info_cache = {}  # type: dict[str, BlockBasicInfo]
_block_tags_cache = {}  # type: dict[str, set[str]]


def get_digging_level(block_id, block_basic_info, default=0):
    # type: (str, BlockBasicInfo, int) -> int
    if block_basic_info.tier is not None:
        return block_basic_info.tier.get("level", 3)
    else:
        block_tags = _block_tags_cache.get(block_id)
        if block_tags is None:
            block_tags = _block_tags_cache[block_id] = set(
                CF.CreateBlockInfo(LEVEL_ID).GetBlockTags(block_id)
            )
        for k, v in DIGGING_LEVEL_MAPPING.items():
            if k in block_tags:
                return v
        return default


def can_dig_same(block_id1, block_id2):
    # type: (str, str) -> bool
    block_basic_info1 = _block_basic_info_cache.get(block_id1)
    if block_basic_info1 is None:
        block_basic_info1 = _block_basic_info_cache[block_id1] = BlockBasicInfo.unmarshal(
            CF.CreateBlockInfo(LEVEL_ID).GetBlockBasicInfo(block_id1)
        )
    block_basic_info2 = _block_basic_info_cache.get(block_id2)
    if block_basic_info2 is None:
        block_basic_info2 = _block_basic_info_cache[block_id2] = BlockBasicInfo.unmarshal(
            CF.CreateBlockInfo(LEVEL_ID).GetBlockBasicInfo(block_id2)
        )
    if (
        block_basic_info1.destroyTime < block_basic_info2.destroyTime
        or block_basic_info2.destroyTime < 0
    ):
        return False
    if block_basic_info2.tier and block_basic_info2.tier.get("digger", 1) != 1:
        return False
    if block_basic_info1.tier is not None and block_basic_info2.tier is not None:
        return block_basic_info1.tier.get("level", 0) >= block_basic_info2.tier.get(
            "level", 255
        )
    res = get_digging_level(block_id1, block_basic_info1) >= get_digging_level(
        block_id2, block_basic_info2
    )
    return res

@Delay(0)
def chain_mine(player_id, dimension_id, block_full_name, poses):
    # type: (str, int, str, list[tuple[int, int, int]]) -> None
    mhitem = CF.CreateItem(player_id).GetPlayerItem(GetMinecraftEnum().ItemPosType.CARRIED, 0, True)
    mhitem = Item.from_dict(mhitem) if mhitem is not None else None
    if mhitem is None or mhitem.id not in MINING_HAMMERS or mhitem.durability is None:
        return
    last_index = len(poses) - 1
    try:
        for i, pos in enumerate(poses):
            block_id = (CF.CreateBlockInfo(LEVEL_ID).GetBlockNew(
                pos,
                dimension_id,
            ) or {}).get("name")
            if block_id is None:
                continue
            if not can_dig_same(block_full_name, block_id):
                continue
            player_digging_poses.setdefault(player_id, set()).add(pos)
            CF.CreateBlockInfo(player_id).PlayerDestoryBlock(pos, True, i == last_index)
    finally:
        player_digging_poses.pop(player_id, None)


@DestroyBlockEvent.Listen()
def onDestroyBlock(event):
    # type: (DestroyBlockEvent) -> None
    if (
        event.playerId in player_digging_poses
        and (event.x, event.y, event.z) in player_digging_poses[event.playerId]
    ):
        return
    mhitem = CF.CreateItem(event.playerId).GetPlayerItem(
        GetMinecraftEnum().ItemPosType.CARRIED,
        0,
        True,
    )
    mhitem = Item.from_dict(mhitem) if mhitem is not None else None
    if mhitem is None or mhitem.id not in MINING_HAMMERS or mhitem.durability is None:
        return
    block_tags = _block_tags_cache.get(event.fullName)
    if block_tags is None:
        block_tags = _block_tags_cache[event.fullName] = set(
            CF.CreateBlockInfo(LEVEL_ID).GetBlockTags(event.fullName)
        )
    if "minecraft:is_pickaxe_item_destructible" not in block_tags:
        block_basic_info = _block_basic_info_cache.get(event.fullName)
        if block_basic_info is None:
            block_basic_info = _block_basic_info_cache[event.fullName] = BlockBasicInfo.unmarshal(
                CF.CreateBlockInfo(LEVEL_ID).GetBlockBasicInfo(event.fullName)
            )
        if (block_basic_info.tier or {}).get("digger") != 1:
            return
    x = event.x
    y = event.y
    z = event.z
    face = event.face
    if face == 0 or face == 1:
        poses = [
            (_x, y, _z)
            for _x in range(x - 1, x + 2)
            for _z in range(z - 1, z + 2)
            if _x != x or _z != z
        ]
    elif face == 2 or face == 3:
        poses = [
            (_x, _y, z)
            for _x in range(x - 1, x + 2)
            for _y in range(y - 1, y + 2)
            if _x != x or _y != y
        ]
    elif face == 4 or face == 5:
        poses = [
            (x, _y, _z)
            for _y in range(y - 1, y + 2)
            for _z in range(z - 1, z + 2)
            if _y != y or _z != z
        ]
    else:
        return
    chain_mine(event.playerId, event.dimensionId, event.fullName, poses)


