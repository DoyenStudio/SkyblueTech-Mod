# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta

from ...common.define import flags
from ...common.define.id_enum import Machinery
from ...common.events.machinery.charger import (
    ChargeItemModelRequest,
    ChargerItemModelUpdate,
)
from ...common.machinery_def.basic import K_PROGRESS
from ...common.machinery_def.charger import (
    K_CHARGE_RF,
    K_CHARGE_RF_MAX,
    STORE_RF_MAX,
)
from ...common.machinery_def.charger import (
    recipes as Recipes,
)
from ...common.utils.block_sync import BlockSync
from .basic import (
    OperationListener,
    Processor,
    RegisterMachine,
    UpgradeControl,
)
from .utils.charge import (
    ChargeItem,
    GetCharge,
    GetIOPower,
)

block_sync = BlockSync(Machinery.CHARGER, side=BlockSync.SIDE_SERVER)


def IsChargeableItem(item):
    # type: (Item | None) -> bool
    "物品是否可充能: NBT 中带有 max_input_power / max_output_power。"
    if item is None:
        return False
    ud = item.userData
    return ud is not None and GetIOPower(ud, -1, -1) != (-1, -1)


@RegisterMachine
class Charger(OperationListener, Processor):
    """
    充电台, 双模式机器:

        - 槽位 0 放入可充能物品时走充能流程 (每 5 tick 从自身储能抽电充入物品);
        - 否则按 `Processor` 的配方逻辑匹配并运行配方。
    """

    block_name = Machinery.CHARGER
    allow_upgraders = frozenset()
    input_slots = (0,)
    output_slots = (1,)
    upgrade_slot_start = 2
    store_rf_max = STORE_RF_MAX
    dump_progress_to_block_entity_data = True
    process_item = True
    recipes = Recipes

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        self.t = 0
        self.charging = False
        self.RefreshMode()

    @SuperExecutorMeta.execute_super
    def OnClick(self, event, extra_datas=None):
        pass

    @SuperExecutorMeta.execute_super
    def OnUnload(self):
        block_sync.discard_block((self.dim, self.x, self.y, self.z))

    def OnTicking(self):
        if not self.charging:
            Processor.OnTicking(self)
            return
        if self.IsActive():
            self.t += 1
            if self.t >= 5:
                self.t = 0
                self.charge_once()

    def RefreshMode(self):
        "按槽位 0 的物品重新判定工作模式, 并同步停机旗与充能进度。"
        item = self.GetSlotItem(0, get_user_data=True)
        if IsChargeableItem(item):
            self.charging = True
            self.charge_rf, self.charge_rf_max = GetCharge(item.userData)
            # 清掉配方残留: 否则会被 NO_RECIPE 卡住, 进度条也会显示上一次配方的旧进度
            if self.current_recipe is not None:
                self.current_recipe = None
                self.ResetProgress()
            self.ResetDeactiveFlags()
            self.SyncChargeProgress()
        else:
            self.charging = False
            self.charge_rf = 0
            self.charge_rf_max = 1
            if item is None:
                if self.current_recipe is not None:
                    self.current_recipe = None
                    self.ResetProgress()
                self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
                self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT)
            else:
                self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT)
                self.recheck_recipe()
        ChargerItemModelUpdate(
            self.x,
            self.y,
            self.z,
            item.id if item is not None else None,
            item.isEnchanted if item is not None else False,
        ).sendMulti(block_sync.get_players((self.dim, self.x, self.y, self.z)))

    def IsValidInput(self, slot, item):
        # type: (int, Item) -> bool
        if self.InUpgradeSlot(slot):
            return UpgradeControl.IsValidInput(self, slot, item)
        if IsChargeableItem(item):
            return slot == 0
        return Processor.IsValidInput(self, slot, item)

    @SuperExecutorMeta.execute_super_with_blacklist(Processor)
    def OnSlotUpdate(self, slot_pos):
        # type: (int) -> None
        if self.InUpgradeSlot(slot_pos):
            UpgradeControl.OnSlotUpdate(self, slot_pos)
            return
        if slot_pos == 0:
            self.RefreshMode()
            return
        if not self.charging:
            Processor.OnSlotUpdate(self, slot_pos)
            return
        if self.GetSlotItem(1) is None:
            # 可能可以输出充能完成的物品了
            slot0 = self.GetSlotItem(0, get_user_data=True)
            if slot0 is not None and self.charge_rf >= self.charge_rf_max:
                self.OutputItem(slot0)
                self.SetSlotItem(0, None)

    def SyncChargeProgress(self):
        "把物品的充能比例写进 st:progress, 让客户端进度条在充能模式下也能推进。"
        self.bdata[K_PROGRESS] = min(
            1.0, float(self.charge_rf) / max(1, self.charge_rf_max)
        )

    def _update_work_status(self):
        # 充电台方块是单贴图模型方块, 未声明 skybluetech:active, 不能写这个方块状态。
        # WorkRenderer 的三个停机旗方法都会调到这里, 覆写成空实现即可屏蔽;
        # 用 execute_super_with_blacklist(WorkRenderer) 是屏蔽不掉的 (见 super_executor.py:93)。
        pass

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
        self.SyncChargeProgress()
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
