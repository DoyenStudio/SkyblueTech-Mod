# coding=utf-8
from ...define.id_enum import Machinery
from .define import CategoryType, Input, MachineRecipe

CATALYST_SLOT = 2


class SmallChemicalReactorRecipe(MachineRecipe):
    """catalyst=Input(...) 指定催化剂；只检查存在，不消耗数量或耐久。"""

    recipe_icon_id = Machinery.SMALL_CHEMICAL_REACTOR

    def __init__(self, inputs=None, outputs=None, power_cost=1, tick_duration=1,
                 inputs_unordered=None, outputs_unordered=None, catalyst=None):
        # 催化剂使用零数量输入，参与匹配但不参与扣料；反序列化也走此处。
        inputs = dict((kind, dict(slots)) for kind, slots in (inputs or {}).items())
        item_inputs = inputs.get(CategoryType.ITEM, {})
        catalyst = catalyst if catalyst is not None else item_inputs.get(CATALYST_SLOT)
        if catalyst is not None:
            inputs.setdefault(CategoryType.ITEM, {})[CATALYST_SLOT] = Input(
                catalyst.id, 0, catalyst.aux, catalyst.is_tag
            )
        for slots in (inputs_unordered or {}).get(CategoryType.ITEM, {}):
            if CATALYST_SLOT in slots:
                raise ValueError("Catalyst slot must use a fixed input")
        for slots in (outputs_unordered or {}).get(CategoryType.ITEM, {}):
            if CATALYST_SLOT in slots:
                raise ValueError("Catalyst slot cannot be an output")
        if CATALYST_SLOT in (outputs or {}).get(CategoryType.ITEM, {}):
            raise ValueError("Catalyst slot cannot be an output")
        MachineRecipe.__init__(self, inputs, outputs, power_cost, tick_duration,
                               inputs_unordered, outputs_unordered)
