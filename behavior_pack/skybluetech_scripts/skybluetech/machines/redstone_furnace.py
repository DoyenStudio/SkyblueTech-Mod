# coding=utf-8
#
from mod.server.blockEntityData import BlockEntityData
from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.api.server.world import GetRecipesByInput
from skybluetech_scripts.tooldelta.plugins.recipe_obj import GetFurnaceRecipe
from ..define import flags
from ..define.machine_config.redstone_furnace import TICK_POWER
from ..ui_sync.machines.redstone_furnace import RedstoneFurnaceUISync
from .basic import AutoSaver, BaseMachine, ItemContainer, GUIControl, SPControl, WorkRenderer, RegisterMachine


def GetFurnaceOutputByInput(item_id, aux_value=0):
    # type: (str, int) -> str | None
    res = GetRecipesByInput(item_id, "furnace", aux_value, maxResultNum=1)
    if len(res) < 1:
        return None
    else:
        return GetFurnaceRecipe(res[0]).output.item_id


@RegisterMachine
class RedstoneFurnace(AutoSaver, GUIControl, ItemContainer, SPControl, WorkRenderer):
    block_name = "skybluetech:redstone_furnace"
    store_rf_max = 8800
    origin_process_ticks = 20 * 8 # 8s
    running_power = TICK_POWER
    input_slots = (0,)
    output_slots = (1,)
    upgrade_slot_start = 2
    upgrade_slots = 4

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        AutoSaver.__init__(self, dim, x, y, z, block_entity_data)
        BaseMachine.__init__(self, dim, x, y, z, block_entity_data)
        ItemContainer.__init__(self, dim, x, y, z, block_entity_data)
        self.sync = RedstoneFurnaceUISync.NewServer(self).Activate()
        self.OnSync()
        self.TryStartNext()

    def OnTicking(self):
        while self.IsActive():
            self.OnSync()
            if self.ProcessOnce():
                self.runOnce()
                self.TryStartNext()
            else:
                break

    def TryStartNext(self, dont_recursive=False):
        input_item = self.GetSlotItem(0)
        output_item = self.GetSlotItem(1)
        if input_item is None:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT)
            if not dont_recursive:
                self.RequireItems()
                self.TryStartNext(dont_recursive=True)
            return
        expected_output = GetFurnaceOutputByInput(input_item.newItemName)
        if expected_output is None:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
            return
        if not self.canOutput(expected_output, output_item):
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL)
            return
                
    def runOnce(self):
        input_item = self.GetSlotItem(0)
        output_item = self.GetSlotItem(1)
        if input_item is None:
            raise ValueError("No input")
        expected_output = GetFurnaceOutputByInput(input_item.newItemName)
        if expected_output is None:
            raise ValueError("Recipe ERROR")
        if not self.canOutput(expected_output, output_item):
            return
        self.finishOnce(input_item, output_item, expected_output)

    def finishOnce(self, input, output, expected_output):
        # type: (Item, Item | None, str) -> None
        input.count -= 1
        self.SetSlotItem(0, input)
        if output is not None:
            output_item = output
            output_item.count += 1
        else:
            output_item = Item(expected_output)
        self.SetSlotItem(1, output_item)

    def canOutput(self, expected_output_item_id, output_slot_item):
        # type: (str, Item | None) -> bool
        return output_slot_item is None or (
            output_slot_item.newItemName == expected_output_item_id
            and not output_slot_item.StackFull()
        )

    def OnSync(self):
        self.sync.storage_rf = self.store_rf 
        self.sync.rf_max = self.store_rf_max
        self.sync.progress_relative = self.GetProcessProgress()
        self.sync.MarkedAsChanged()

    def IsValidInput(self, slot, item):
        # type: (int, Item) -> bool
        return True

    def OnSlotUpdate(self, slot_pos):
        # type: (int) -> None
        if slot_pos == 1:
            return
        input_item = self.GetSlotItem(0)
        output_item = self.GetSlotItem(1)
        if input_item is None:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT)
            return
        else:
            self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT)
        expected_output = GetFurnaceOutputByInput(input_item.newItemName)
        if expected_output is None:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
            return
        else:
            self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
        if not self.canOutput(expected_output, output_item):
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL)
            return
        else:
            self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL)

    def SetDeactiveFlag(self, flag):
        # type: (int) -> None
        SPControl.SetDeactiveFlag(self, flag)
        WorkRenderer.SetDeactiveFlag(self, flag)

    def OnUnload(self):
        # type: () -> None
        AutoSaver.OnUnload(self)
        BaseMachine.OnUnload(self)
        GUIControl.OnUnload(self)