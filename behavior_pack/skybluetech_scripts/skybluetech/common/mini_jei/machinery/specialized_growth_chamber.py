# coding=utf-8
from ...define.id_enum import Machinery
from ...machinery_def.hydroponic_bed import POWER_COST
from .define import CategoryType, Input, MachineRecipe

CATALYST_SLOTS = (1, 2)


class SpecializedGrowthChamberRecipe(MachineRecipe):
    """固定槽位培养配方；槽 1、2 必须存在，但不消耗数量或耐久。"""

    recipe_icon_id = Machinery.SPECIALIZED_GROWTH_CHAMBER

    def __init__(self, inputs=None, outputs=None, power_cost=POWER_COST,
                 tick_duration=1, inputs_unordered=None, outputs_unordered=None):
        if power_cost != POWER_COST:
            raise ValueError("Specialized growth chamber power cost must be %s" % POWER_COST)
        if tick_duration <= 0:
            raise ValueError("Specialized growth chamber duration must be positive")
        if inputs_unordered or outputs_unordered:
            raise ValueError("Specialized growth chamber requires fixed recipe slots")
        inputs = dict((kind, dict(slots)) for kind, slots in (inputs or {}).items())
        outputs = dict((kind, dict(slots)) for kind, slots in (outputs or {}).items())
        for side, allowed in ((inputs, {CategoryType.ITEM: (0, 1, 2), CategoryType.FLUID: (0,)}),
                              (outputs, {CategoryType.ITEM: (3,), CategoryType.FLUID: (1,)})):
            for kind, slots in side.items():
                if kind not in allowed or any(slot not in allowed[kind] for slot in slots):
                    raise ValueError("Invalid specialized growth chamber recipe slots")
        item_inputs = inputs.get(CategoryType.ITEM, {})
        for slot in CATALYST_SLOTS:
            catalyst = item_inputs.get(slot)
            if catalyst is None:
                raise ValueError("Specialized growth chamber requires item slot %s" % slot)
            item_inputs[slot] = Input(catalyst.id, 0, catalyst.aux, catalyst.is_tag)
        for kind, slots in inputs.items():
            for slot, element in slots.items():
                if kind == CategoryType.ITEM and slot in CATALYST_SLOTS:
                    continue
                if element.count <= 0:
                    raise ValueError("Consumed recipe inputs must have positive amounts")
        for kind, slots in outputs.items():
            for element in slots.values():
                if element.count <= 0 or not 0 <= element.prob <= 1:
                    raise ValueError("Recipe outputs require positive amounts and valid probabilities")
                if kind == CategoryType.FLUID and element.prob != 1:
                    raise ValueError("Specialized growth chamber fluid output must be guaranteed")
        MachineRecipe.__init__(self, inputs, outputs, POWER_COST, tick_duration)
