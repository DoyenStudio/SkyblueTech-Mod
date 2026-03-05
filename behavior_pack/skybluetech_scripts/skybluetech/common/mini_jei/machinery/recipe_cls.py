# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui import UBaseCtrl
from skybluetech_scripts.tooldelta.extensions.allitems_getter import GetItemsByTag
from ..core import Recipe, Input, Output, CategoryType, ItemDisplayer, FluidDisplayer


class MachineRecipe(Recipe):
    render_progress = True

    def __init__(self, inputs, outputs, power_cost, tick_duration):
        # type: (dict[str, dict[int, Input]], dict[str, dict[int, Output]], int, int) -> None
        Recipe.__init__(self, inputs, outputs)
        self.power_cost = power_cost
        self.tick_duration = tick_duration

    def __repr__(self):
        return "MachineRecipe(%s, %s, %d, %d)" % (
            self.inputs,
            self.outputs,
            self.power_cost,
            self.tick_duration,
        )

    def __hash__(self):
        return hash((tuple(self.inputs), tuple(self.outputs)))

    def RenderInit(self, panel):
        # type: (UBaseCtrl) -> None
        input_items = self.inputs.get("item", {})
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
        output_items = self.outputs.get("item", {})
        for slot, input in output_items.items():
            item_id = input.id
            ItemDisplayer(panel["slot%d" % slot], Item(item_id, count=int(input.count)))
        input_fluids = self.inputs.get("fluid", {})
        if input_fluids:
            max_input_fluid_volume = max(
                input_fluids.values(), key=lambda x: x.count
            ).count
        for slot, input in input_fluids.items():
            FluidDisplayer(
                panel["fluid%d" % slot], input.id, input.count, max_input_fluid_volume
            )
        output_fluids = self.outputs.get("fluid", {})
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

    def RenderUpdate(self, panel, render_ticks):
        # type: (UBaseCtrl, int) -> None
        if not self.render_progress:
            return
        td = self.tick_duration * 3
        p = (render_ticks * 2.0) % td / td
        panel["progress/mask"].asImage().SetSpriteClipRatio("fromRightToLeft", 1 - p)
