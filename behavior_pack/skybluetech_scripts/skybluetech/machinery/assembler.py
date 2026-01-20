# coding=utf-8
#
from mod.server.blockEntityData import BlockEntityData
from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.api.server import UpdateBlockStates, GetBlockName
from skybluetech_scripts.tooldelta.events.server import ServerBlockUseEvent, BlockNeighborChangedServerEvent
from ..define import flags
from ..define.events.machinery.assembler import *
from ..define.facing import DXYZ_FACING, FACING_EN
from ..define.id_enum.machinery import ASSEMBLER as MACHINE_ID
from ..machinery_def.assembler import *
from ..tools.upgraders.register import UpdateObjectData
from ..utils.action_commit import SafeGetMachine
from ..utils.lore import GetLorePos, SetLoreAtPos
from ..ui_sync.machinery.assembler import AssemblerUISync
from ..transmitters.wire.logic import isWire
from .basic import GUIControl, UpgradeControl, RegisterMachine

def g(dic, key):
    return dic[key]["__value__"]


@RegisterMachine
class Assembler(GUIControl, UpgradeControl):
    block_name = MACHINE_ID
    store_rf_max = 100000
    energy_io_mode = (0, 0, 0, 0, 0, 0)

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        UpgradeControl.__init__(self, dim, x, y, z, block_entity_data)
        self.sync = AssemblerUISync.NewServer(self).Activate()
        self.power = 0
        self.delay = 20
        self.lis = []  # type: list[tuple[str, str, int]]
        self.updateList()
        self.OnSync()

    def AddPower(self, rf, max_limit=None, passed=None):
        res = UpgradeControl.AddPower(self, rf, max_limit, passed)
        if self.store_rf > 0 and self.HasDeactiveFlag(flags.DEACTIVE_FLAG_POWER_LACK):
            self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_POWER_LACK)
        return res

    def OnPlaced(self, _):
        for dx, dy, dz in DXYZ_FACING.keys():
            facing_en = FACING_EN[DXYZ_FACING[dx, dy, dz]]
            bname = GetBlockName(self.dim, (self.x + dx, self.y + dy, self.z + dz))
            if not bname:
                continue
            connectToWire = isWire(bname)
            UpdateBlockStates(
                self.dim,
                (self.x, self.y, self.z),
                {"skybluetech:connection_" + facing_en: connectToWire},
            )

    def OnNeighborChanged(self, event):
        # type: (BlockNeighborChangedServerEvent) -> None
        dx = event.neighborPosX - self.x
        dy = event.neighborPosY - self.y
        dz = event.neighborPosZ - self.z
        facing_en = FACING_EN[DXYZ_FACING[dx, dy, dz]]
        if facing_en not in {"south", "north", "east", "west"}:
            return
        connectToWire = isWire(event.toBlockName)
        UpdateBlockStates(
            self.dim,
            (self.x, self.y, self.z),
            {"skybluetech:connection_" + facing_en: connectToWire}
        )
        

    def OnTryActivate(self):
        # type: () -> None
        self.ResetDeactiveFlags()

    def OnClick(self, event):
        # type: (ServerBlockUseEvent) -> None
        GUIControl.OnClick(self, event)
        AssemblerUpgradersUpdate(self.lis).send(event.playerId)

    def OnSync(self):
        self.sync.storage_rf = self.store_rf
        self.sync.rf_max = self.store_rf_max
        self.sync.MarkedAsChanged()

    def OnSlotUpdate(self, slot_pos):
        # type: (int) -> None
        self.updateList()
        AssemblerUpgradersUpdate(self.lis).sendMulti(self.sync.GetPlayersInSync())

    def OnUnload(self):
        # type: () -> None
        UpgradeControl.OnUnload(self)
        GUIControl.OnUnload(self)

    def IsValidInput(self, slot, item):
        # type: (int, Item) -> bool
        if self.InUpgradeSlot(slot):
            return UpgradeControl.IsValidInput(self, slot, item)
        if slot == 0:
            return (
                item.userData is not None
                and "skybluetech:assembler_available" in item.GetBasicInfo().tags
            )
        elif slot == 1:
            return (
                item.userData is not None
                and TAG_UPGRADER in item.GetBasicInfo().tags
            )
        else:
            return False

    def updateList(self):
        it = self.GetSlotItem(0, get_user_data=True)
        if it is None:
            self.lis = [("minecraft:barrier", "请放入待改装道具", -1)]
            return
        upgraders = getUpgraders(it)
        if not upgraders:
            self.lis = [("minecraft:barrier", "未安装任何升级", -1)]
            return
        self.lis = [(id, id, 0) for id in upgraders]

    def onPushUpgrader(self):
        slot0_item = self.GetSlotItem(0, get_user_data=True)
        slot1_item = self.GetSlotItem(1, get_user_data=True)
        if (
            slot0_item is None
            or slot1_item is None
            or TAG_CAN_UPGRADE not in slot0_item.GetBasicInfo().tags
            or TAG_UPGRADER not in slot1_item.GetBasicInfo().tags
        ):
            return
        upgraders = getUpgraders(slot0_item)
        if slot1_item.id in upgraders:
            return
        if not self.canAddNewUpgrader(slot0_item, upgraders, slot1_item):
            return
        upgraders[slot1_item.id] = slot1_item
        setUpgraders(slot0_item, upgraders)
        self.SetSlotItem(1, None)
        self.SetSlotItem(0, slot0_item)
        self.updateList()
        self.OnSync()

    def onPullUpgrader(self, index):
        # type: (int) -> None
        if index < 0 or index >= len(self.lis):
            return
        slot0_item = self.GetSlotItem(0, get_user_data=True)
        slot1_item = self.GetSlotItem(1, get_user_data=True)
        if (
            slot0_item is None
            or slot1_item is not None
            or TAG_CAN_UPGRADE not in slot0_item.GetBasicInfo().tags
        ):
            return
        upid_to_pull = self.lis[index][0]
        upgraders = getUpgraders(slot0_item)
        if upid_to_pull not in upgraders:
            return
        self.SetSlotItem(1, upgraders.pop(upid_to_pull))
        setUpgraders(slot0_item, upgraders)
        self.SetSlotItem(0, slot0_item)
        self.updateList()
        self.OnSync()

    def canAddNewUpgrader(self, item, exist_upgraders, upgrader):
        # type: (Item, dict[str, Item], Item) -> bool
        if upgrader.id in exist_upgraders:
            return False
        item_tags = item.GetBasicInfo().tags
        for utag in upgrader.GetBasicInfo().tags:
            if not utag.startswith(UPGRADER_TAG_PREFIX):
                continue
            reflect_tag = OBJECT_PREFIX + utag[UPGRADER_TAG_PREFIX_L:]
            if reflect_tag is not None and reflect_tag in item_tags:
                break
        else:
            return False
        return getMaxUpgradersCount(item) > len(exist_upgraders)


def getUpgraders(item):
    # type: (Item) -> dict[str, Item]
    ud = item.userData
    if ud is None:
        raise ValueError("Get upgraders from invalid item " + item.newItemName)
    data = {}  # type: dict[str, Item]
    for up_id, up_ud in ud[K_UD_UPGRADERS].items():
        data[up_id] = Item(up_id, userData=up_ud)
    return data


def setUpgraders(item, data):
    # type: (Item, dict[str, Item]) -> None
    ud = item.userData
    if ud is None:
        raise ValueError("Set upgraders to invalid item " + item.newItemName)
    ud[K_UD_UPGRADERS] = {
        k: v.userData
        for k, v in data.items()
    }
    SetLoreAtPos(ud, GetLorePos(ud, "object_upgraders"), formatUpgraders(data))
    UpdateObjectData(item)

def formatUpgraders(data):
    # type: (dict[str, Item]) -> str
    if not data:
        return "§r§6◆ 未安装任何升级§f"
    output = "§r§7一一一一一一一一一一一一\n§e◆ 已安装的升级："
    for it in data.values():
        name = it.GetBasicInfo().itemName
        output += "\n  §a" + name + "§f"
    output += "\n§7一一一一一一一一一一一一"
    return output

def getMaxUpgradersCount(item):
    # type: (Item) -> int
    ud = item.userData
    if ud is None:
        return 0
    return g(ud, K_UD_MAX_UPGRADERS)


@AssemblerActionRequest.Listen()
def onHandleAction(event):
    # type: (AssemblerActionRequest) -> None
    m = SafeGetMachine(event.x, event.y, event.z, event.player_id)
    if not isinstance(m, Assembler):
        return
    if event.action == ACTION_PULL_UPGRADER:
        if not isinstance(event.index, int):
            return
        m.onPullUpgrader(event.index)
    elif event.action == ACTION_PUSH_UPGRADER:
        m.onPushUpgrader()
