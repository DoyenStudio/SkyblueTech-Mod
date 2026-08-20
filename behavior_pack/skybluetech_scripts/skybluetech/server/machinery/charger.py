# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta

from ...common.define import flags
from ...common.define.id_enum.machinery import Machinery
from ...common.events.machinery.charger import (
    ChargeItemModelRequest,
    ChargerItemModelUpdate,
)
from ...common.machinery_def.charger import (
    K_CHARGE_RF,
    K_CHARGE_RF_MAX,
    STORE_RF_MAX,
)
from ...common.utils.block_sync import BlockSync
from .basic import GUIControl, OperationListener, RegisterMachine, UpgradeControl
from .utils.charge import (
    ChargeItem,
    GetCharge,
    GetIOPower,
)

block_sync = BlockSync(Machinery.CHARGER, side=BlockSync.SIDE_SERVER)


@RegisterMachine
class Charger(GUIControl, OperationListener, UpgradeControl):
    block_name = Machinery.CHARGER
    allow_upgrader_tags = {"skybluetech:upgraders/charger"}
    input_slots = (0,)
    output_slots = (1,)
    upgrade_slot_start = 2
    store_rf_max = STORE_RF_MAX

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        self.stored_item = None
        self._charge_rf = 0
        self._charge_rf_max = 1
        self.t = 0

    @SuperExecutorMeta.execute_super
    def OnClick(self, event, extra_datas=None):
        pass

    @SuperExecutorMeta.execute_super
    def OnUnload(self):
        block_sync.discard_block((self.dim, self.x, self.y, self.z))

    def OnTicking(self):
        if self.IsActive():
            self.t += 1
            if self.t >= 5:
                self.t = 0
                self.charge_once()

    def IsValidInput(self, slot, item):
        # type: (int, Item) -> bool
        if slot != 0:
            return False
        return not (
            item.userData is None or GetIOPower(item.userData, -1, -1) == (-1, -1)
        )

    @SuperExecutorMeta.execute_super
    def OnSlotUpdate(self, slot_pos):
        # type: (int) -> None
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
                ChargerItemModelUpdate(self.x, self.y, self.z, None).sendMulti(
                    block_sync.get_players((self.dim, self.x, self.y, self.z)),
                )
                return
            ud = charge_item.userData
            if ud is None:
                print("[WARN] Charger: ud is None: " + charge_item.newItemName)
                return
            self.charge_rf, self.charge_rf_max = GetCharge(ud)
            self.ResetDeactiveFlags()
            ChargerItemModelUpdate(
                self.x, self.y, self.z, charge_item.id, charge_item.isEnchanted
            ).sendMulti(
                block_sync.get_players((self.dim, self.x, self.y, self.z)),
            )

    def charge_once(self):
        if self.charge_rf_max == 0 or self.charge_rf_max == 1:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT)
            return
        elif self.store_rf == 0:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_POWER_LACK)
            return
        charged_item = self.GetSlotItem(0)
        if charged_item is None:
            return
        self.store_rf, _in, self.charge_rf = ChargeItem(
            self.store_rf, charged_item, times=5
        )
        self.SetSlotItem(0, charged_item)
        if self.charge_rf >= self.charge_rf_max:
            if self.GetSlotItem(1) is None:
                charge_item = self.GetSlotItem(0, get_user_data=True)
                if charge_item is None:
                    return  # TODO
                it = self.OutputItem(charge_item)
                if it is None:
                    self.SetSlotItem(0, None)
                else:
                    self.SetDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL)

    @property
    def charge_rf(self):
        # type: () -> int
        return self._charge_rf

    @charge_rf.setter
    def charge_rf(self, value):
        # type: (int) -> None
        self.bdata[K_CHARGE_RF] = self._charge_rf = value

    @property
    def charge_rf_max(self):
        # type: () -> int
        return self._charge_rf_max

    @charge_rf_max.setter
    def charge_rf_max(self, value):
        # type: (int) -> None
        self.bdata[K_CHARGE_RF_MAX] = self._charge_rf_max = value


@Charger.ForOperation(ChargeItemModelRequest)
def onItemModelRequest(event, machine):
    # type: (ChargeItemModelRequest, Charger) -> None
    it = machine.GetSlotItem(0)
    if it is None:
        item_id = None
        enchanted = False
    else:
        item_id = it.id
        enchanted = it.isEnchanted
    ChargerItemModelUpdate(machine.x, machine.y, machine.z, item_id, enchanted).send(
        event.player_id
    )
