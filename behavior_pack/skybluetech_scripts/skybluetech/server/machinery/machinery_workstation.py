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
from ...common.machinery_def.machinery_workstation import (
    recipes as Recipes,
    K_CRAFTING_PROGRESS,
    K_OUTPUT_ITEM_ID,
    K_NEED_TOOL,
    get_pincer_level,
    get_wrench_level,
)
from ..machinery.utils.charge import ChargeEnough, GetCharge, GetPowerCost, UpdateCharge
from ..tools.actions.utils import MakeItemUseless
from .basic import BaseMachine, RegisterMachine, GUIControl, ItemContainer, OperationListener

K_CRAFT_TIMES = "craft_times"
ItemPosType = GetMinecraftEnum().ItemPosType


@RegisterMachine
class MachineryWorkstation(BaseMachine, GUIControl, ItemContainer, OperationListener):
    block_name = Machinery.MACHINERY_WORKSTATION
    input_slots = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    output_slots = (11,)

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        self.current_recipe = None
        self.need_tool = False
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
        self.bdata[K_NEED_TOOL] = self.need_tool

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
        self.need_tool = False
        slotitems = self.GetInputSlotItems()
        pincer_item = slotitems.get(10)
        wrench_item = slotitems.get(9)
        pincer_level = get_pincer_level(pincer_item) if pincer_item else 0
        wrench_level = get_wrench_level(wrench_item) if wrench_item else 0
        if pincer_item is not None and self._is_charged_tool_without_charge(pincer_item):
            pincer_level = 0
        if wrench_item is not None and self._is_charged_tool_without_charge(wrench_item):
            wrench_level = 0
        for rcp in Recipes:
            input_items = rcp.input_items
            materials_ok = True
            for slot in range(9):
                slotitem = slotitems.get(slot)
                if slot not in input_items:
                    if slotitem is not None:
                        materials_ok = False
                        break
                else:
                    input = input_items[slot]
                    if (
                        slotitem is None
                        or not input.match_item_id(slotitem.id)
                        or slotitem.count < input.count
                    ):
                        materials_ok = False
                        break
            if not materials_ok:
                continue
            # 材料已凑齐(合成格与某配方完全匹配), 仅工具等级不足时提示放入工具
            if pincer_level < rcp.pincer_level or wrench_level < rcp.wrench_level:
                self.need_tool = True
            else:
                self.current_recipe = rcp
            break
        if not init and last_recipe != self.current_recipe:
            self.craft_times = 0

    @staticmethod
    def _is_charged_tool_without_charge(tool_item):
        # type: (Item) -> bool
        """充能工具余量不足一次消耗时视为不可用。"""
        ud = tool_item.userData
        if ud is None or GetPowerCost(ud) <= 0:
            return False
        return not ChargeEnough(ud)

    def _consume_tool_use(self, tool_item, craft_strength):
        # type: (Item, float) -> tuple[Item | None, bool]
        """消耗一次工具使用(耐久或充能), 返回 (处理后物品, 是否可继续制造)。

        蔚蓝充能工具每次使用消耗 st:cost_rf 对应充能(默认 1000RF),
        余量不足一次消耗时不可继续使用; 耗尽的充能工具转为 _useless 形态。
        """
        ud = tool_item.userData
        if ud is not None and GetPowerCost(ud) > 0:
            if self._is_charged_tool_without_charge(tool_item):
                return tool_item, False
            if random.random() < craft_strength:
                cur_charge, _ = GetCharge(ud)
                UpdateCharge(tool_item, cur_charge - GetPowerCost(ud))
                if not ChargeEnough(ud):
                    MakeItemUseless(tool_item)
            return tool_item, True
        orig_durability = tool_item.durability
        if orig_durability is None:
            return tool_item, False
        if random.random() < craft_strength:
            tool_item.durability = max(0, orig_durability - 1)
            if tool_item.durability <= 0:
                tool_item = None
        return tool_item, True

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
            pincer_item, usable = self._consume_tool_use(
                pincer_item, event.craft_strength
            )
            if not usable:
                return
            if pincer_item is None:
                SetCommand(
                    'execute as "%s" at @s positioned %d %d %d run playsound random.break'
                    % (GetNameById(event.player_id), self.x, self.y, self.z)
                )
            self.SetSlotItem(10, pincer_item)
        if recipe.wrench_level > 0:
            if wrench_item is None:
                return
            wrench_item, usable = self._consume_tool_use(
                wrench_item, event.craft_strength
            )
            if not usable:
                return
            if wrench_item is None:
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


@MachineryWorkstation.ForOperation(MachineryWorkstationDoCraft)
def onDoCraft(event, machine):
    # type: (MachineryWorkstationDoCraft, MachineryWorkstation) -> None
    machine.on_craft(event)


@MachineryWorkstation.ForOperation(MachineryWorkstationTransferRecipe)
def onTransferRecipe(event, machine):
    # type: (MachineryWorkstationTransferRecipe, MachineryWorkstation) -> None
    machine.transfer_recipe_items(event.player_id, event.output_item_id)
