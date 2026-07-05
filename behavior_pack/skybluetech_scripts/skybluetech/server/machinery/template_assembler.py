# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.api.server import GetSeed
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from skybluetech_scripts.tooldelta.utils import nbt
from ...common.define.id_enum import (
    Machinery,
    INSCRIBING_TEMPLATE,
)

MACHINE_ID = Machinery.TEMPLATE_ASSEMBLER
from ...common.events.machinery.template_assembler import (
    TemplateAssemblerUpdateRecipeEvent,
    TemplateAssemblerUpdateRecipeEvent2,
)
from ...common.misc.inscribing_template import K_UD_TEMPLATE_GRAPH
from ...common.machinery_def.template_assembler import (
    TemplateAssemblerRecipe,
    TemplateAssemblerRecipesCollection,
    recipes as Recipes,
    GetResultByTemplateGraph,
    STORE_RF_MAX,
    TEMPLATE_SLOT_INDEX,
    K_TEMPLATE_ITEM_COUNT,
    K_TEMPLATE_ITEM_ID,
    K_TEMPLATE_ITEM_IS_TAG,
    K_TEMPLATE_ITEMS,
)
from .basic import MultiFluidContainer, Processor, RegisterMachine


@RegisterMachine
class TemplateAssembler(MultiFluidContainer, Processor):
    block_name = MACHINE_ID
    store_rf_max = STORE_RF_MAX
    dump_progress_to_block_entity_data = True
    process_item = True
    recipes = TemplateAssemblerRecipesCollection()  # type: TemplateAssemblerRecipesCollection
    input_slots = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    output_slots = (11,)
    upgrade_slot_start = 12
    upgrade_slots = 4

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        self.update_template_slot()
        self.sync_recipe()
        self.recheck_recipe()

    @SuperExecutorMeta.execute_super
    def OnAddedFluid(self, slot, fluid_id, fluid_volume, is_final):
        pass

    @SuperExecutorMeta.execute_super
    def OnReducedFluid(self, slot, fluid_id, reduced_fluid_volume, is_final):
        pass

    def IsValidInput(self, slot, item):
        # type: (int, Item) -> bool
        if slot == TEMPLATE_SLOT_INDEX:
            return item.id == INSCRIBING_TEMPLATE
        else:
            return Processor.IsValidInput(self, slot, item)

    @SuperExecutorMeta.execute_super
    def OnSlotUpdate(self, slot_pos):
        # type: (int) -> None
        if slot_pos != TEMPLATE_SLOT_INDEX:
            return
        self.update_template_slot()
        self.recheck_recipe()
        self.sync_recipe()
        # TODO: 重复发送两遍 BUG: 只发一遍可能丢包 fuck netease
        TemplateAssemblerUpdateRecipeEvent().sendMulti(self.ui_sync.GetPlayersInSync())
        TemplateAssemblerUpdateRecipeEvent2().sendMulti(self.ui_sync.GetPlayersInSync())

    def update_template_slot(self):
        item = self.GetSlotItem(TEMPLATE_SLOT_INDEX, get_user_data=True)
        if item is None or item.userData is None:
            self.recipes = TemplateAssemblerRecipesCollection()  # no recipe
            return
        graph = item.userData.get(K_UD_TEMPLATE_GRAPH, None)
        if graph is None:
            self.recipes = TemplateAssemblerRecipesCollection()  # no recipe
            return
        graph = [nbt.ValueOf(i) for i in graph]
        result_item_id = GetResultByTemplateGraph(graph, GetSeed())
        if result_item_id is None:
            self.recipes = TemplateAssemblerRecipesCollection()  # no recipe
        else:
            self.recipes = TemplateAssemblerRecipesCollection(
                Recipes.recipes_mapping[result_item_id]
            )

    def sync_recipe(self):
        sync_list = [{K_TEMPLATE_ITEM_ID: None}] * 9  # type: list[dict]
        if self.recipes.recipes_mapping:
            recipe = next(iter(self.recipes.recipes_mapping.values()))
            if not isinstance(recipe, TemplateAssemblerRecipe):
                return
            for i in range(9):
                item_input = recipe.input_items.get(i)
                if item_input is None:
                    continue
                sync_list[i] = {
                    K_TEMPLATE_ITEM_ID: item_input.id,
                    K_TEMPLATE_ITEM_IS_TAG: item_input.is_tag,
                    K_TEMPLATE_ITEM_COUNT: item_input.count,
                }
        self.bdata[K_TEMPLATE_ITEMS] = sync_list
