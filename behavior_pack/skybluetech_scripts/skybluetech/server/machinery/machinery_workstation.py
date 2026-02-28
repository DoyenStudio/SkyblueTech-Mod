# coding=utf-8
import random
from mod.server.blockEntityData import BlockEntityData
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.api.server import SetCommand, GetNameById
from ...common.events.machinery.machinery_workstation import (
    MachineryWorkstationDoCraft,
)
from ...common.define.id_enum.machinery import MACHINERY_WORKSTATION as MACHINE_ID
from ...common.machinery_def.machinery_workstation import (
    recipes as Recipes,
    get_pincer_level,
    get_wrench_level,
)
from ...common.ui_sync.machinery.machinery_workstation import MachineryWorkstationUISync
from .utils.action_commit import SafeGetMachine
from .basic import BaseMachine, RegisterMachine, GUIControl, ItemContainer

K_CRAFT_TIMES = "craft_times"


@RegisterMachine
class MachineryWorkstation(BaseMachine, GUIControl, ItemContainer):
    block_name = MACHINE_ID
    input_slots = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    output_slots = (11,)

    def __init__(self, dim, x, y, z, block_entity_data):
        BaseMachine.__init__(self, dim, x, y, z, block_entity_data)
        ItemContainer.__init__(self, dim, x, y, z, block_entity_data)
        self.sync = MachineryWorkstationUISync.NewServer(self).Activate()
        self.load_recipe(init=True)
        self.OnSync()

    def OnUnload(self):
        BaseMachine.OnUnload(self)
        GUIControl.OnUnload(self)

    def OnSync(self):
        self.sync.progress = (
            float(self.craft_times) / self.current_recipe.craft_times
            if self.current_recipe
            else 0
        )
        self.sync.output_item_id = (
            self.current_recipe.output_item_id if self.current_recipe else None
        )
        self.sync.MarkedAsChanged()

    def OnSlotUpdate(self, slot_pos):
        # type: (int) -> None
        self.load_recipe()
        self.OnSync()

    def load_recipe(self, init=False):
        if not init:
            last_recipe = self.current_recipe
        else:
            last_recipe = None
        self.current_recipe = None
        slotitems = self.GetInputSlotItems()
        pincer_item = slotitems.get(10)
        wrench_item = slotitems.get(9)
        pincer_level = get_pincer_level(pincer_item) if pincer_item else 0
        wrench_level = get_wrench_level(wrench_item) if wrench_item else 0
        for rcp in Recipes:
            input_items = rcp.input_items
            if pincer_level < rcp.pincer_level or wrench_level < rcp.wrench_level:
                continue
            ok = True
            for slot in range(9):
                slotitem = slotitems.get(slot)
                if slot not in input_items:
                    if slotitem is not None:
                        ok = False
                        break
                else:
                    input = input_items[slot]
                    if (
                        slotitem is None
                        or not input.match_item_id(slotitem.id)
                        or slotitem.count < input.count
                    ):
                        ok = False
                        break
            if ok:
                self.current_recipe = rcp
                break
        if not init and last_recipe != self.current_recipe:
            self.craft_times = 0

    def on_craft(self, event):
        # type: (MachineryWorkstationDoCraft) -> None
        recipe = self.current_recipe
        if recipe is None:
            return
        slotitems = self.GetInputSlotItems()
        pincer_item = slotitems.get(10)
        wrench_item = slotitems.get(9)
        if recipe.pincer_level > 0:
            if pincer_item is None:
                return
            orig_durability = pincer_item.durability
            if orig_durability is None:
                return
            if random.random() < event.craft_strength:
                pincer_item.durability = max(0, orig_durability - 1)
                if pincer_item.durability <= 0:
                    pincer_item = None
            self.SetSlotItem(10, pincer_item)
        if recipe.wrench_level > 0:
            if wrench_item is None:
                return
            orig_durability = wrench_item.durability
            if orig_durability is None:
                return
            if random.random() < event.craft_strength:
                wrench_item.durability = max(0, orig_durability - 1)
                if wrench_item.durability <= 0:
                    wrench_item = None
            self.SetSlotItem(9, wrench_item)
        self.craft_times += 1
        if self.craft_times >= recipe.craft_times:
            output_slot_item = self.GetSlotItem(11, get_user_data=True)
            if output_slot_item is not None and (
                not output_slot_item.CanMerge(Item(recipe.output_item_id))
                or output_slot_item.StackFull()
            ):
                return
            self.craft_times = 0
            for slot, input in recipe.input_items.items():
                slotitem = slotitems[slot]
                slotitem.count -= input.count
                self.SetSlotItem(slot, slotitem)
            if output_slot_item is None:
                self.SetSlotItem(11, Item(recipe.output_item_id))
            else:
                output_slot_item.count += 1
                self.SetSlotItem(11, output_slot_item)
        sound = [
            "random.anvil_use",
            "block.barrel.open",
            "block.grindstone.use",
            "block.stonecutter.use",
        ][int(round(random.random() * 3))]
        SetCommand(
            'execute as "%s" at @s positioned %d %d %d run playsound %s'
            % (GetNameById(event.player_id), self.x, self.y, self.z, sound)
        )
        self.OnSync()

    @property
    def craft_times(self):
        # type: () -> int
        return self.bdata[K_CRAFT_TIMES] or 0

    @craft_times.setter
    def craft_times(self, value):
        # type: (int) -> None
        self.bdata[K_CRAFT_TIMES] = value


@MachineryWorkstationDoCraft.Listen()
def onDoCraft(event):
    # type: (MachineryWorkstationDoCraft) -> None
    m = SafeGetMachine(event.x, event.y, event.z, event.player_id)
    if not isinstance(m, MachineryWorkstation):
        return
    m.on_craft(event)
