# coding=utf-8
from ...define.id_enum import INSCRIBING_TEMPLATE
from ..core import (
    Recipe,
    Input,
    Output,
    CategoryType,
    UnmarshalOrderedInputs,
    UnmarshalOrderedOutputs,
)


class IndustrialResearchingRecipe(Recipe):
    def __init__(
        self,
        require_items,  # type: list[Input]
        require_exp_level,  # type: int
        result_item_id,  # type: str
    ):
        Recipe.__init__(
            self,
            {
                CategoryType.ITEM: {i: v for i, v in enumerate(require_items)},
                CategoryType.EXP_LV: {0: Input(CategoryType.EXP_LV, require_exp_level)},
            },
            {
                CategoryType.ITEM: {
                    len(require_items): Output(result_item_id),
                    len(require_items) + 1: Output(INSCRIBING_TEMPLATE),
                }
            },
        )
        self.require_items = require_items
        self.require_exp_level = require_exp_level
        self.result_item_id = result_item_id

    def __hash__(self):
        return hash(
            (
                tuple(
                    (item.id, item.count, item.aux, item.is_tag)
                    for item in self.require_items
                ),
                self.require_exp_level,
                self.result_item_id,
            )
        )

    @classmethod
    def Unmarshal(cls, data):
        inputs = UnmarshalOrderedInputs(data["inputs"])
        outputs = UnmarshalOrderedOutputs(data["outputs"])
        require_items = [
            item for slot, item in sorted(inputs[CategoryType.ITEM].items())
        ]
        return cls(
            require_items=require_items,
            require_exp_level=inputs[CategoryType.EXP_LV][0].count,
            result_item_id=outputs[CategoryType.ITEM][len(require_items)].id,
        )
