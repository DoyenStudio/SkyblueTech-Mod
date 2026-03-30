# coding=utf-8
from skybluetech_scripts.tooldelta.api.common import ExecLater
from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.utils.nbt import NBT2Py
from skybluetech_scripts.tooldelta.extensions.recipe_obj import (
    GetCraftingRecipe,
    CraftingRecipeRes,
    UnorderedCraftingRecipeRes,
    RecipeInput,
    RecipeOutput,
)
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ...common.define import flags
from ...common.events.machinery.electric_crafter import (
    ElectricCrafterUpdateRecipe,
)
from ...common.define.id_enum.items import CRAFTING_TEMPLATE
from ...common.define.id_enum.machinery import ELECTRIC_CRAFTER as MACHINE_ID
from ...common.ui_sync.machinery.electric_crafter import ElectricCrafterUISync
from .basic import GUIControl, UpgradeControl, RegisterMachine

TEMPLATE_SLOT = 12


@RegisterMachine
class ElectricCrafter(GUIControl, UpgradeControl):
    origin_process_ticks = 60
    running_power = 35
    block_name = MACHINE_ID
    input_slots = tuple(range(9))
    output_slots = tuple(range(9, 12))
    upgrade_slot_start = TEMPLATE_SLOT + 1
    energy_io_mode = (0, 0, 0, 0, 0, 0)
    allow_upgrader_tags = {
        "skybluetech:upgraders/speed",
        "skybluetech:upgraders/energy",
    }

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        self.sync = ElectricCrafterUISync.NewServer(self).Activate()
        self.try_update_template()
        self.CallSync()

    def OnTicking(self):
        while self.IsActive():
            self.CallSync()
            if self.ProcessOnce():
                self.run_once()
                self.detect_next()
            else:
                break

    @SuperExecutorMeta.execute_super
    def OnClick(self, event, extra_datas=None):
        ExecLater(0.1, self.notify_crafting_update)

    def OnSync(self):
        self.sync.rf = self.store_rf
        self.sync.rf_max = self.store_rf_max
        self.sync.progress = self.GetProcessProgress()
        self.sync.MarkedAsChanged()

    @SuperExecutorMeta.execute_super
    def OnUnload(self):
        pass

    def IsValidInput(self, slot, item):
        # type: (int, Item) -> bool
        if self.InUpgradeSlot(slot):
            return UpgradeControl.IsValidInput(self, slot, item)
        elif slot == TEMPLATE_SLOT:
            return item.id == CRAFTING_TEMPLATE
        else:
            return self.check_crafting_input_valid(slot, item)

    @SuperExecutorMeta.execute_super
    def OnSlotUpdate(self, slot):
        # type: (int) -> None
        if slot == TEMPLATE_SLOT:
            self.try_update_template()
            self.notify_crafting_update()
        elif slot < 9:
            self.separate_items()
            self.detect_next()
        elif self.InUpgradeSlot(slot):
            pass
        else:
            self.detect_next()

    def check_crafting_input_valid(self, slot, item):
        # type: (int, Item) -> bool
        if self.template is None or self.rcp_items is None:
            return False
        rcp_slot = self.rcp_items[slot]
        if rcp_slot is None:
            return False
        return item.id in rcp_slot.item_ids

    def try_update_template(self):
        self.template = None
        self.rcp_items = None
        self.res_items = None
        it = self.GetSlotItem(TEMPLATE_SLOT, get_user_data=True)
        if it is None:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
            return
        ud = it.userData
        if ud is None:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
            return
        recipe_dict = NBT2Py(ud.get("st:template_recipe"))
        if not isinstance(recipe_dict, dict):
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
            return
        self.template = GetCraftingRecipe(recipe_dict)
        self.rcp_items, self.res_items = get_slot_items_by_recipe(self.template)
        self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)

    def detect_next(self):
        if not self.run_once(check_only=True):
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT)
        else:
            self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT)
            self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL)

    def run_once(self, check_only=False):
        if self.template is None:
            return False
        recipe_slots, res_items = get_slot_items_by_recipe(self.template)
        slotitems_new_count = {}  # type: dict[int, Item | None]
        for i in range(9):
            item = self.GetSlotItem(i)
            rcp_slot = recipe_slots[i]
            if rcp_slot is None:
                continue
            if item is None:
                return False
            if item.count < rcp_slot.count or item.id not in rcp_slot.item_ids:
                return False
            it_new = item.copy()
            it_new.count -= rcp_slot.count
            slotitems_new_count[i] = it_new if it_new.count > 0 else None
        output_items = [
            Item(out.item_id, out.aux_value, out.count) for out in self.template.result
        ]
        if not self.CanOutputItems(output_items):
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL)
            return False
        if check_only:
            return True
        for slot, item in slotitems_new_count.items():
            self.SetSlotItem(slot, item)
        for item in output_items:
            self.OutputItem(item)
        return True

    def separate_items(self):
        if self.template is None:
            return
        slotitems = {}  # type: dict[int, tuple[Item | None, RecipeInput]]
        rcpitems, _ = get_slot_items_by_recipe(self.template)
        for slot, rcp_input in enumerate(rcpitems):
            if rcp_input is None:
                continue
            slotitems[slot] = (self.GetSlotItem(slot), rcp_input)
        for slot, (item, rcp_input) in slotitems.copy().items():
            if item is not None:
                continue
            for _item, _rcp_input in slotitems.copy().values():
                if _rcp_input != rcp_input or _item is None or _item.count <= 1:
                    continue
                _item.count -= 1
                item_copy = _item.copy()
                item_copy.count = 1
                slotitems[slot] = (item_copy, rcp_input)
        for slot, (item, _) in slotitems.items():
            self.SetSlotItem(slot, item)

    def notify_crafting_update(self):
        if self.rcp_items is not None:
            ElectricCrafterUpdateRecipe([
                (i.item_ids[0], i.aux_value) if i else None for i in self.rcp_items
            ]).sendMulti(self.sync.GetPlayersInSync())
        else:
            ElectricCrafterUpdateRecipe([None] * 9).sendMulti(
                self.sync.GetPlayersInSync()
            )


def get_slot_items_by_recipe(
    recipe,  # type: CraftingRecipeRes | UnorderedCraftingRecipeRes
):
    res = [None] * 9  # type: list[RecipeInput | None]
    if isinstance(recipe, CraftingRecipeRes):
        pat = recipe.pattern
        for i, pat_line in enumerate(pat):
            for j, pat_item in enumerate(pat_line):
                if pat_item == " ":
                    continue
                res[i * 3 + j] = recipe.pattern_key[pat_item]
    else:
        items = sorted(recipe.inputs, key=lambda x: x.item_ids[0])
        for i, item in enumerate(items):
            res[i] = item
    return res, recipe.result
