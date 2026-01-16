# coding=utf-8
from mod.server.blockEntityData import BlockEntityData
from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.api.server import GetRecipeByRecipeId
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault
from skybluetech_scripts.tooldelta.extensions.recipe_obj import (
    GetCraftingRecipe,
    CraftingRecipeRes,
    UnorderedCraftingRecipeRes,
    RecipeInput,
)
from ..define import flags
from ..define.id_enum.items import CRAFTING_TEMPLATE
from ..define.id_enum.machinery import ELECTRIC_CRAFTER as MACHINE_ID
from ..ui_sync.machines.electric_crafter import ElectricCrafterUISync
from ..utils.action_commit import SafeGetMachine
from .basic import GUIControl, UpgradeControl, RegisterMachine

TEMPLATE_SLOT = 17


@RegisterMachine
class ElectricCrafter(GUIControl, UpgradeControl):
    block_name = MACHINE_ID
    input_slots = tuple(range(9))
    output_slots = tuple(range(9, 17))
    upgrade_slot_start = TEMPLATE_SLOT + 1
    energy_io_mode = (0, 0, 0, 0, 0, 0)

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        UpgradeControl.__init__(self, dim, x, y, z, block_entity_data)
        self.sync = ElectricCrafterUISync.NewServer(self).Activate()
        self.try_update_template()

    def OnTicking(self):
        while self.IsActive():
            self.OnSync()
            if self.ProcessOnce():
                self.run_once()
                self.detect_next()
            else:
                break

    def OnUnload(self):
        GUIControl.OnUnload(self)
        UpgradeControl.OnUnload(self)

    def IsValidInput(self, slot, item):
        # type: (int, Item) -> bool
        if self.InUpgradeSlot(slot):
            return UpgradeControl.IsValidInput(self, slot, item)
        elif slot == 18:
            return item.id == CRAFTING_TEMPLATE
        else:
            return self.check_crafting_input_valid(slot, item)

    def OnSlotUpdate(self, slot) -> None:
        # type: (int) -> None
        if slot == TEMPLATE_SLOT:
            self.try_update_template()
        elif slot < 9:
            self.detect_next()
        elif self.InUpgradeSlot(slot):
            UpgradeControl.OnSlotUpdate(self, slot)

    def check_crafting_input_valid(self, slot, item):
        # type: (int, Item) -> bool
        if self.template is None:
            return False
        rcp_items = get_slot_items_by_recipe(self.template)
        rcp_slot = rcp_items[slot]
        if rcp_slot is None:
            return False
        if rcp_slot.is_tag:
            return rcp_slot.item_id in item.GetBasicInfo().tags
        else:
            return rcp_slot.item_id == item.id

    def try_update_template(self):
        self.template = None
        it = self.GetSlotItem(TEMPLATE_SLOT, get_user_data=True)
        if it is None:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
            return
        ud = it.userData
        if ud is None:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
            return
        recipe_tag = GetValueWithDefault(ud, "tag", None)
        recipe_id = GetValueWithDefault(ud, "crafting_id", None)
        if recipe_tag is None or recipe_id is None:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
            return
        self.template = GetCraftingRecipe(GetRecipeByRecipeId(recipe_id, recipe_tag))
        self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)

    def detect_next(self):
        if not self.run_once(check_only=True):
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT)
        else:
            self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT)

    def run_once(self, check_only=False):
        if self.template is None:
            return False
        recipe_slots = get_slot_items_by_recipe(self.template)
        slotitems_new_count = {} # type: dict[int, Item | None]
        for i in range(9):
            item = self.GetSlotItem(i)
            rcp_slot = recipe_slots[i]
            if rcp_slot is None:
                continue
            if item is None:
                return False
            if (
                item.count < rcp_slot.count
                or (
                    rcp_slot.item_id not in item.GetBasicInfo().tags
                    if rcp_slot.is_tag else item.id != rcp_slot.item_id
                )
            ):
                return False
            it_new = item.copy()
            it_new.count -= rcp_slot.count
            slotitems_new_count[i] = (it_new if it_new.count > 0 else None)
        if check_only:
            return True
        output_items = [
            Item(out.item_id, out.aux_value, out.count)
            for out in self.template.result
        ]
        if not self.CanOutputItems(output_items):
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL)
            return False
        for slot, item in slotitems_new_count.items():
            self.SetSlotItem(slot, item)
        for item in output_items:
            self.OutputItem(item)
        return True
        

def get_slot_items_by_recipe(
    recipe # type: CraftingRecipeRes | UnorderedCraftingRecipeRes
):
    res = [None] * 9 # type: list[RecipeInput | None]
    if isinstance(recipe, CraftingRecipeRes):
        pat = recipe.pattern
        for i, pat_line in enumerate(pat):
            for j, pat_item in enumerate(pat_line):
                if pat_item == " ":
                    continue
                res[i * 3 + j] = recipe.pattern_key[pat_item]
    else:
        items = sorted(recipe.inputs, key=lambda x: x.item_id)
        for i, item in enumerate(items):
            res[i] = item
    return res
