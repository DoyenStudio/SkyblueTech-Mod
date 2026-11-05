# coding=utf-8
from ..utils.recipe_plan import get_recipe_plan

_UNREAD = object()
_slot_read_methods = set()


def accepts_slot_reads(method):
    """声明实例方法可复用本批读取；写入前须 clear()，调用其他钩子须走 call()。"""
    _slot_read_methods.add(method)
    return method


class SlotReads(object):
    """一次同步结算中的槽位读取；旧钩子可修改库存，调用前丢弃快照。"""

    def __init__(self, machine):
        self.machine = machine
        self.clear()

    def clear(self):
        self._inputs = self._outputs = None
        self._plan = None

    def call(self, method, *args, **kwargs):
        # 仅显式登记的方法接收新参数，使用 functools.wraps 的旧覆写也走旧签名。
        if getattr(method, "__func__", None) in _slot_read_methods:
            return method(*args, slot_reads=self, **kwargs)
        self.clear()
        return method(*args, **kwargs)

    def inputs(self):
        if self._inputs is None:
            self._inputs = self.machine.GetInputSlotItems()
        return self._inputs

    def outputs(self):
        if self._outputs is None:
            self._outputs = self.machine.GetOutputSlotItems()
        return self._outputs

    def plan_for(self, recipe):
        if self._plan is None or self._plan.recipe is not recipe:
            self._plan = get_recipe_plan(recipe)
            self._item_inputs = self._item_outputs = _UNREAD
            self._fluid_inputs = self._fluid_outputs = _UNREAD
        return self._plan

    def allocate_inputs(self, recipe):
        plan = self.plan_for(recipe)
        if self._item_inputs is _UNREAD:
            self._item_inputs = plan.plan_item_inputs(self.inputs())
        return self._item_inputs

    def allocate_outputs(self, recipe):
        plan = self.plan_for(recipe)
        if self._item_outputs is _UNREAD:
            self._item_outputs = plan.plan_item_outputs(self.outputs(), self.machine.item_output_slots)
        return self._item_outputs

    def allocate_fluid_inputs(self, recipe):
        plan = self.plan_for(recipe)
        if self._fluid_inputs is _UNREAD:
            self._fluid_inputs = plan.plan_fluid_inputs(self.machine.fluids)
        return self._fluid_inputs

    def allocate_fluid_outputs(self, recipe):
        plan = self.plan_for(recipe)
        if self._fluid_outputs is _UNREAD:
            self._fluid_outputs = plan.plan_fluid_outputs(self.machine.fluids, self.machine.fluid_output_slots)
        return self._fluid_outputs
