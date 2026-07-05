# coding=utf-8
import random
from mod.server.extraServerApi import GetMinecraftEnum
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.api.server import (
    SetCommand,
    GetNameById,
    GetAllInventoryItems,
    SetPlayerAllItems,
    GiveItem,
)
from ...common.events.machinery.machinery_workstation import (
    MachineryWorkstationDoCraft,
    MachineryWorkstationTransferRecipe,
)
from ...common.define.id_enum.machinery import Machinery
MACHINE_ID = Machinery.MACHINERY_WORKSTATION
from ...common.machinery_def.machinery_workstation import (
    recipes as Recipes,
    K_CRAFTING_PROGRESS,
    K_OUTPUT_ITEM_ID,
    get_pincer_level,
    get_wrench_level,
)
from .utils.action_commit import SafeGetMachine
from .basic import BaseMachine, RegisterMachine, GUIControl, ItemContainer

K_CRAFT_TIMES = "craft_times"
ItemPosType = GetMinecraftEnum().ItemPosType


@RegisterMachine
class MachineryWorkstation(BaseMachine, GUIControl, ItemContainer):
    block_name = MACHINE_ID
    input_slots = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    output_slots = (11,)

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        self.current_recipe = None
        self.load_recipe(init=True)
        self.CallSync()

    @SuperExecutorMeta.execute_super
    def OnUnload(self):
        pass

    def OnSync(self):
        self.bdata[K_CRAFTING_PROGRESS] = (
            float(self.craft_times) / self.current_recipe.craft_times
            if self.current_recipe
            else 0
        )
        self.bdata[K_OUTPUT_ITEM_ID] = (
            self.current_recipe.output_item_id if self.current_recipe else None
        )

    def OnSlotUpdate(self, slot_pos):
        # type: (int) -> None
        self.load_recipe()
        self.CallSync()

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
                    SetCommand(
                        'execute as "%s" at @s positioned %d %d %d run playsound random.break'
                        % (GetNameById(event.player_id), self.x, self.y, self.z)
                    )
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
                    SetCommand(
                        'execute as "%s" at @s positioned %d %d %d run playsound random.break'
                        % (GetNameById(event.player_id), self.x, self.y, self.z)
                    )
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
        self.CallSync()

    @property
    def craft_times(self):
        # type: () -> int
        return self.bdata[K_CRAFT_TIMES] or 0

    @craft_times.setter
    def craft_times(self, value):
        # type: (int) -> None
        self.bdata[K_CRAFT_TIMES] = value

    def transfer_recipe_items(self, player_id, output_item_id):
        # type: (str, str) -> None
        """点击配方: 先把合成格现有物品(以及不满足需求的工具)归还玩家背包,
        再从背包填充合成格, 并自动放入等级足够的扳手/钳。物品不足时只放入已有的部分。"""
        recipe = None
        for rcp in Recipes:
            if rcp.output_item_id == output_item_id:
                recipe = rcp
                break
        if recipe is None:
            return
        # 扳手槽=9, 钳槽=10
        tool_reqs = (
            (9, recipe.wrench_level, get_wrench_level),
            (10, recipe.pincer_level, get_pincer_level),
        )
        # 归还合成格现有物品(归还失败则保留, 避免背包满时丢物品)
        for slot in range(9):
            cur = self.GetSlotItem(slot, get_user_data=True)
            if cur is not None and GiveItem(player_id, cur):
                self.SetSlotItem(slot, None)
        for tool_slot, need_level, level_of in tool_reqs:
            if need_level <= 0:
                continue
            cur = self.GetSlotItem(tool_slot, get_user_data=True)
            if cur is None or level_of(cur) >= need_level:
                continue
            if GiveItem(player_id, cur):
                self.SetSlotItem(tool_slot, None)
        inv_items = {
            slot: item.copy()
            for slot, item in GetAllInventoryItems(player_id, get_userdata=True).items()
        }
        changed_inv = {}  # type: dict[tuple[int, int], Item]
        for slot, input in recipe.input_items.items():
            if self.GetSlotItem(slot, get_user_data=True) is not None:
                continue
            target_id = None
            for it in inv_items.values():
                if it.count > 0 and input.match_item_id(it.id):
                    target_id = it.id
                    break
            if target_id is None:
                continue
            need = input.count
            placed = None
            for inv_slot, it in inv_items.items():
                if need <= 0:
                    break
                if it.count <= 0 or it.id != target_id:
                    continue
                take = min(it.count, need)
                if placed is None:
                    placed = it.copy()
                    placed.count = take
                else:
                    placed.count += take
                it.count -= take
                need -= take
                changed_inv[(ItemPosType.INVENTORY, inv_slot)] = (
                    it.copy() if it.count > 0 else Item("minecraft:air", count=0)
                )
            if placed is not None and placed.count > 0:
                self.SetSlotItem(slot, placed)
        # 放入等级足够的扳手/钳, 优先最低满足等级以保留高级工具
        for tool_slot, need_level, level_of in tool_reqs:
            if need_level <= 0:
                continue
            if self.GetSlotItem(tool_slot, get_user_data=True) is not None:
                continue
            best_slot = None
            best_level = None
            for inv_slot, it in inv_items.items():
                if it.count <= 0:
                    continue
                lv = level_of(it)
                if lv >= need_level and (best_level is None or lv < best_level):
                    best_slot = inv_slot
                    best_level = lv
            if best_slot is None:
                continue
            it = inv_items[best_slot]
            tool_item = it.copy()
            tool_item.count = 1
            it.count -= 1
            changed_inv[(ItemPosType.INVENTORY, best_slot)] = (
                it.copy() if it.count > 0 else Item("minecraft:air", count=0)
            )
            self.SetSlotItem(tool_slot, tool_item)
        if changed_inv:
            SetPlayerAllItems(player_id, changed_inv)
        self.load_recipe()
        self.CallSync()


@MachineryWorkstationDoCraft.Listen()
def onDoCraft(event):
    # type: (MachineryWorkstationDoCraft) -> None
    m = SafeGetMachine(event.x, event.y, event.z, event.player_id)
    if not isinstance(m, MachineryWorkstation):
        return
    m.on_craft(event)


@MachineryWorkstationTransferRecipe.Listen()
def onTransferRecipe(event):
    # type: (MachineryWorkstationTransferRecipe) -> None
    m = SafeGetMachine(event.x, event.y, event.z, event.player_id)
    if not isinstance(m, MachineryWorkstation):
        return
    m.transfer_recipe_items(event.player_id, event.output_item_id)
