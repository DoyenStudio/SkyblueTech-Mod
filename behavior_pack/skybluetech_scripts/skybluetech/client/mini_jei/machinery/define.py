# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui.elem_comp import UBaseCtrl
from skybluetech_scripts.tooldelta.extensions.allitems_getter import GetItemsByTag
from skybluetech_scripts.skybluetech.common.mini_jei import Recipe
from skybluetech_scripts.skybluetech.common.mini_jei.machinery import (
    MachineRecipeBase,
    MachineRecipe,
    GeneratorRecipe,
)
from ...ui.recipe_checker.render_utils import ItemDisplayer
from ...ui.recipe_checker.render_utils_advanced import FluidDisplayer
from ..core import RecipeRenderer


class MachineRecipeRendererBase(RecipeRenderer):
    def __init__(self, recipe):
        # type: (Recipe) -> None
        RecipeRenderer.__init__(self, recipe)
        self.recipe = recipe

    def RenderInit(self, panel):
        # type: (UBaseCtrl) -> None
        recipe = self.recipe
        input_items = recipe.inputs.get("item", {})
        for slot, input in input_items.items():
            item = input.id
            is_tag = input.is_tag
            if is_tag:
                try:
                    item_id = next(iter(GetItemsByTag(item)))
                except StopIteration:
                    raise ValueError("tag2item not found: " + item)
            else:
                item_id = item
            ItemDisplayer(
                panel["slot%d" % slot],
                Item(item_id, count=int(input.count)),
                tag=item if is_tag else None,
            )
        output_items = recipe.outputs.get("item", {})
        for slot, input in output_items.items():
            item_id = input.id
            ItemDisplayer(panel["slot%d" % slot], Item(item_id, count=int(input.count)))
        input_fluids = recipe.inputs.get("fluid", {})
        if input_fluids:
            max_input_fluid_volume = max(
                input_fluids.values(), key=lambda x: x.count
            ).count
        for slot, input in input_fluids.items():
            FluidDisplayer(
                panel["fluid%d" % slot], input.id, input.count, max_input_fluid_volume
            )
        output_fluids = recipe.outputs.get("fluid", {})
        if output_fluids:
            max_output_fluid_volume = max(
                output_fluids.values(), key=lambda x: x.count
            ).count
        for slot, output in output_fluids.items():
            FluidDisplayer(
                panel["fluid%d" % slot],
                output.id,
                output.count,
                max_output_fluid_volume,
            )


class MachineRecipeRenderer(MachineRecipeRendererBase):
    render_progress = True

    def __init__(self, recipe):
        # type: (MachineRecipe) -> None
        MachineRecipeRendererBase.__init__(self, recipe)
        self.recipe = recipe

    def RenderUpdate(self, panel, render_ticks):
        # type: (UBaseCtrl, int) -> None
        if not self.render_progress:
            return
        td = self.recipe.tick_duration * 3
        p = (render_ticks * 2.0) % td / td
        panel["progress/mask"].asImage().SetSpriteClipRatio("fromRightToLeft", 1 - p)


class GeneratorRecipeRenderer(MachineRecipeRendererBase):
    def __init__(self, recipe):
        # type: (GeneratorRecipe) -> None
        MachineRecipeRendererBase.__init__(self, recipe)
        self.recipe = recipe

    def RenderInit(self, panel):
        # type: (UBaseCtrl) -> None
        from ....client.ui.machinery.utils import FormatRF
        from ....client.ui.recipe_checker.render_utils import RFOutputDisplayer

        MachineRecipeRendererBase.RenderInit(self, panel)
        self.rf_output_renderer = RFOutputDisplayer(
            panel["output_power"], self.recipe.output_power * self.recipe.tick_duration
        )
        panel["tick_power"].asLabel().SetText(FormatRF(self.recipe.output_power) + "/t")


__all__ = [
    "MachineRecipe",
    "MachineRecipeBase",
    "GeneratorRecipe",
]
