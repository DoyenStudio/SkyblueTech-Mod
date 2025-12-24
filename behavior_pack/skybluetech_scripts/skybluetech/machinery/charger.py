# coding=utf-8
#
from mod.server.blockEntityData import BlockEntityData
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.api.server import (
    GetPlayersInDim,
    GetPos,
    GetPlayerDimensionId as SGetPlayerDim,
)
from skybluetech_scripts.tooldelta.api.client import (
    GetPlayerDimensionId as CGetPlayerDim,
    CreateDropItemModelEntity,
    SetDropItemTransform,
    DeleteClientDropItemEntity,
)
from skybluetech_scripts.tooldelta.events.notify import (
    NotifyToClients,
    NotifyToClient,
    NotifyToServer,
)
from skybluetech_scripts.tooldelta.events.client import (
    ModBlockEntityLoadedClientEvent,
    ModBlockEntityRemoveClientEvent,
)
from ..define import flags
from ..machinery_def.charger import CHARGE_SPEED
from ..define.events.charger import ChargerItemModelUpdate, ChargeItemModelRequest
from ..ui_sync.machines.charger import ChargerUISync
from ..utils.charge import GetCharge, UpdateCharge, K_STORE_RF, K_STORE_RF_MAX
from .basic import AutoSaver, GUIControl, UpgradeControl, RegisterMachine
from .pool import GetMachineStrict


@RegisterMachine
class Charger(AutoSaver, GUIControl, UpgradeControl):
    block_name = "skybluetech:charger"
    allow_upgrader_tags = {"skybluetech:upgraders/charger"}
    input_slots = (0,)
    output_slots = (1,)
    upgrade_slot_start = 2
    store_rf_max = 10000

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        AutoSaver.__init__(self, dim, x, y, z, block_entity_data)
        UpgradeControl.__init__(self, dim, x, y, z, block_entity_data)
        self.sync = ChargerUISync.NewServer(self).Activate()
        self.stored_item = None
        self.charge_rf = 0
        self.charge_rf_max = 1
        self.charge_speed = CHARGE_SPEED
        self.t = 0
        self.OnSync()

    def OnClick(self, evt):
        # 被打开时才更新充能信息
        self.updateCharge()
        GUIControl.OnClick(self, evt)

    def OnUnload(self):
        AutoSaver.OnUnload(self)
        GUIControl.OnUnload(self)
        UpgradeControl.OnUnload(self)
        self.updateCharge()

    def OnTicking(self):
        if self.IsActive():
            self.chargeOnce()
            self.t += 1
            if self.t >= 5:
                self.t = 0
                if self.sync.AnyoneInSync():
                    self.updateCharge()
            self.OnSync()

    def OnSync(self):
        self.sync.storage_rf = self.store_rf
        self.sync.rf_max = self.store_rf_max
        self.sync.progress_relative = self.charge_rf / self.charge_rf_max
        self.sync.MarkedAsChanged()

    def IsValidInput(self, slot, item):
        # type: (int, Item) -> bool
        if slot != 0:
            return False
        if item.userData is None or (
            K_STORE_RF not in item.userData or K_STORE_RF_MAX not in item.userData
        ):
            return False
        return True

    def OnSlotUpdate(self, slot_pos):
        # type: (int) -> None
        if self.InUpgradeSlot(slot_pos):
            return UpgradeControl.OnSlotUpdate(self, slot_pos)
        if slot_pos == 1:
            if self.GetSlotItem(1) is None:
                # 可能可以输出充能完成的物品了
                slot0 = self.GetSlotItem(0, get_user_data=True)
                if slot0 is not None and self.charge_rf >= self.charge_rf_max:
                    self.OutputItem(slot0)
                    self.SetSlotItem(0, None)
        elif slot_pos == 0:
            # 充能物发生变化
            charge_item = self.GetSlotItem(0, get_user_data=True)
            if charge_item is None:
                self.charge_rf = 0
                self.charge_rf_max = 1
                self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT)
                NotifyToClients(
                    GetPlayersInDim(self.dim),
                    ChargerItemModelUpdate(self.x, self.y, self.z, None),
                )
                return
            ud = charge_item.userData
            if ud is None:
                print("[WARN] Charger: ud is None: " + charge_item.newItemName)
                return
            self.charge_rf, self.charge_rf_max = GetCharge(ud)
            self.updateCharge()
            self.ResetDeactiveFlags()
            NotifyToClients(
                GetPlayersInDim(self.dim),
                ChargerItemModelUpdate(
                    self.x, self.y, self.z, charge_item.id, charge_item.isEnchanted
                ),
            )

    def updateCharge(self):
        charge_item = self.GetSlotItem(0, get_user_data=True)
        if charge_item is None or charge_item.userData is None:
            # if charge_item is not None:
            #     print ("Charge userdata=None", charge_item.userData is None)
            return
        UpdateCharge("", charge_item, self.charge_rf)
        self.SetSlotItem(0, charge_item)

    def chargeOnce(self):
        if self.charge_rf_max == 0 or self.charge_rf_max == 1:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT)
            return
        elif self.store_rf == 0:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_POWER_LACK)
            return
        charge_power = min(self.store_rf, max(self.charge_rf_max - self.charge_rf, 0))
        self.store_rf -= charge_power
        self.charge_rf += charge_power
        if self.charge_rf >= self.charge_rf_max:
            self.updateCharge()
            if self.GetSlotItem(1) is None:
                charge_item = self.GetSlotItem(0, get_user_data=True)
                if charge_item is None:
                    return  # TODO
                it = self.OutputItem(charge_item)
                if it is None:
                    self.SetSlotItem(0, None)
                else:
                    self.SetDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL)


cli_loading_machines = set()  # type: set[tuple[int, int, int]]
cli_models = {}  # type: dict[tuple[int, int, int], str]


@ChargerItemModelUpdate.Listen()
def onModelUpdate(event):
    # type: (ChargerItemModelUpdate) -> None
    pos = (event.x, event.y, event.z)
    if pos not in cli_loading_machines:
        return
    model_id = cli_models.get(pos)
    if model_id is not None:
        DeleteClientDropItemEntity(model_id)
    if event.item_id is not None:
        model_id = cli_models[pos] = CreateDropItemModelEntity(
            CGetPlayerDim(), pos, Item(event.item_id)
        )
        SetDropItemTransform(model_id, (event.x+0.4, event.y+0.5, event.z+0.3), (90, 0, 0))


@ModBlockEntityLoadedClientEvent.Listen()
def onModBlockLoaded(event):
    # type: (ModBlockEntityLoadedClientEvent) -> None
    pos = (event.posX, event.posY, event.posZ)
    cli_loading_machines.add(pos)
    # item_id
    NotifyToServer(ChargeItemModelRequest(event.posX, event.posY, event.posZ))


@ModBlockEntityRemoveClientEvent.Listen()
def onModBlockRemoved(event):
    # type: (ModBlockEntityRemoveClientEvent) -> None
    pos = (event.posX, event.posY, event.posZ)
    cli_loading_machines.discard(pos)
    model_id = cli_models.get(pos)
    if model_id is not None:
        DeleteClientDropItemEntity(cli_models.pop(pos))


@ChargeItemModelRequest.Listen()
def onItemModelRequest(event):
    # type: (ChargeItemModelRequest) -> None
    x = event.x
    y = event.y
    z = event.z
    if not isinstance(x, int) or not isinstance(y, int) or not isinstance(z, int):
        return
    posx, posy, posz = GetPos(event.pid)
    if abs(posx - x) + abs(posy - y) + abs(posz - z) > 64:
        return
    m = GetMachineStrict(SGetPlayerDim(event.pid), x, y, z)
    if not isinstance(m, Charger):
        return
    it = m.GetSlotItem(0)
    if it is None:
        item_id = None
        enchanted = False
    else:
        item_id = it.id
        enchanted = it.isEnchanted
    NotifyToClient(event.pid, ChargerItemModelUpdate(x, y, z, item_id, enchanted))
