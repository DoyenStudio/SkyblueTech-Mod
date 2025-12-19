# coding=utf-8
from collections import deque
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.events.server import ServerPlayerTryDestroyBlockEvent
from skybluetech_scripts.tooldelta.internal import ServerComp
from skybluetech_scripts.tooldelta.api.timer import Delay
from skybluetech_scripts.tooldelta.api.server import GetBlockName
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault
from ...utils.charge import GetCharge, GetChargeCost
from .register import RegisterBlockDestroyCallback
from .utils import GetUpgraderLevel

ID = "skybluetech:obj_upgrader_veinminer"

veining = set() # type: set[tuple[int, int, int, int]]

def bfsVeinMiner(dim, _x, _y, _z, block_id, max_limit):
    # type: (int, int, int, int, str, int) -> deque[tuple[int, int, int, int]]
    res = deque()  # type: deque[tuple[int, int, int, int]]
    scanned = set() # type: set[tuple[int, int, int, int]]
    remainings = deque([(dim, _x, _y, _z)])
    run_count = 0
    while remainings:
        _, x, y, z = remainings.popleft()
        posdata = (dim, x, y, z)
        scanned.add(posdata)
        if GetBlockName(dim, (x, y, z)) == block_id:
            res.append(posdata)
            run_count += 1
            if run_count > max_limit:
                break
            for nx in range(x-1, x+2):
                for ny in range(y-1, y+2):
                    for nz in range(z-1, z+2):
                        next_pos = (dim, nx, ny, nz)
                        if next_pos != posdata and next_pos not in scanned:
                            remainings.append(next_pos)
    return res


def onVeinMine(event, item, item_ud, upgrader_ud):
    # type: (ServerPlayerTryDestroyBlockEvent, Item, dict, dict) -> None
    global veining
    if (event.dimensionId, event.x, event.y, event.z) in veining:
        return
    vein_blocks = set()
    for arg in upgrader_ud.get("st:vein_blocks", []):
        vein_blocks.add(arg["__value__"])
    if event.fullName not in vein_blocks:
        return
    setting_max_vein_blocks = GetValueWithDefault(upgrader_ud, "st:max_chain", 64)
    charge, _ = GetCharge(item_ud)
    charge_cost = GetChargeCost(item_ud)
    max_vein_blocks = min(setting_max_vein_blocks, charge // charge_cost)
    blocks = bfsVeinMiner(event.dimensionId, event.x, event.y, event.z, event.fullName, max_vein_blocks)
    if not blocks:
        return
    digfunc = ServerComp.CreateBlockInfo(event.playerId).PlayerDestoryBlock
    veining |= set(blocks)
    delayBreakBlock(event.playerId, blocks, event.fullName, digfunc)
    # last_idx = len(blocks) - 1
    # for i, (x, y, z) in enumerate(blocks):
    #     digfunc((x, y, z), sendInv=i==last_idx)
    #     charge -= charge_cost
    # # TODO!!!: 此时有可能造成双倍扣除能量
    # UpdateCharge(event.playerId, item, charge)
    # SpawnItemToPlayerCarried(event.playerId, item)

# @Delay(0)
def delayBreakBlock(
    player_id, # type: str
    blocks, # type: deque[tuple[int, int, int, int]]
    block_id, # type: str
    digfunc
):
    if not blocks:
        return
    dim, x, y, z = blocks.popleft()
    cur_block = GetBlockName(dim, (x, y, z))
    if cur_block == block_id:
        digfunc((x, y, z), sendInv=not blocks)
    veining.discard((dim, x, y, z))
    delayBreakBlock(player_id, blocks, block_id, digfunc)


RegisterBlockDestroyCallback(ID, onVeinMine)
