# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.skybluetech.common.mini_jei.core import CategoryType

from skybluetech_scripts.skybluetech.server.machinery.utils.recipe_allocation import (
    allocate,
    allocate_outputs,
)


def _compile_entries(ordered, unordered):
    entries = {}
    for category, slot_elements in (ordered or {}).items():
        entries[category] = [
            ((slot,), element) for slot, element in sorted(slot_elements.items())
        ]
    for category, groups in (unordered or {}).items():
        category_entries = entries.setdefault(category, [])
        for slots, elements in sorted(groups.items()):
            category_entries.extend((slots, element) for element in elements)
    return entries


def _requirements(entries, as_amount, outputs=False, allowed_slots=None):
    requirements = []
    for slots, element in entries:
        if allowed_slots is not None:
            slots = tuple(slot for slot in slots if slot in allowed_slots)
        amount = as_amount(element.count)
        if outputs and (element.prob <= 0 or amount <= 0):
            amount = 0
        requirements.append((slots, amount))
    return requirements


def _element_signature(element):
    return (
        id(element), element.id, element.count, element.aux,
        getattr(element, "is_tag", False), getattr(element, "prob", 1),
    )


def _side_signature(ordered, unordered):
    return (
        tuple(
            (category, tuple(
                (slot, _element_signature(element))
                for slot, element in sorted(elements.items())
            ))
            for category, elements in sorted((ordered or {}).items())
        ),
        tuple(
            (category, tuple(
                (slots, tuple(_element_signature(element) for element in elements))
                for slots, elements in sorted(groups.items())
            ))
            for category, groups in sorted((unordered or {}).items())
        ),
    )


def _recipe_signature(recipe):
    return (
        _side_signature(recipe.inputs, recipe.inputs_unordered),
        _side_signature(recipe.outputs, recipe.outputs_unordered),
    )


class RecipePlan(object):
    """缓存配方编译信息；内容变动时重建，不保留库存快照或分配结果。"""

    def __init__(self, recipe, signature=None):
        self.recipe = recipe
        self._signature = _recipe_signature(recipe) if signature is None else signature
        self.inputs = _compile_entries(recipe.inputs, recipe.inputs_unordered)
        self.outputs = _compile_entries(recipe.outputs, recipe.outputs_unordered)
        self._input_slots = {}
        self._input_match_cache = {}
        for category, entries in self.inputs.items():
            slot_entries = self._input_slots[category] = {}
            self._input_match_cache[category] = [{} for _ in entries]
            for index, (slots, _) in enumerate(entries):
                for slot in slots:
                    slot_entries.setdefault(slot, []).append(index)
        self._item_input_requirements = _requirements(
            self.inputs.get(CategoryType.ITEM, []), int
        )
        self._fluid_input_requirements = _requirements(
            self.inputs.get(CategoryType.FLUID, []), float
        )
        self._item_output_templates = {}

    def _matches_input(self, category, index, item_id, aux):
        cache = self._input_match_cache[category][index]
        key = (item_id, aux)
        result = cache.get(key)
        if result is None:
            element = self.inputs[category][index][1]
            result = element.match_item_id(item_id, aux)
            cache[key] = result
        return result

    def input_matches(self, category, slot, item_id, aux=0):
        for index in self._input_slots.get(category, {}).get(slot, ()):
            if self._matches_input(category, index, item_id, aux):
                return True
        return False

    def plan_item_inputs(self, items):
        capacities = {
            slot: item.count for slot, item in items.items() if item is not None
        }

        def accepts(index, slot):
            item = items.get(slot)
            return item is not None and self._matches_input(
                CategoryType.ITEM, index, item.id, item.newAuxValue
            )

        return allocate(self._item_input_requirements, capacities, accepts)

    def plan_fluid_inputs(self, fluids):
        capacities = {slot: fluid.volume for slot, fluid in fluids.items()}

        def accepts(index, slot):
            fluid = fluids.get(slot)
            return (
                fluid is not None
                and fluid.fluid_id is not None
                and self._matches_input(CategoryType.FLUID, index, fluid.fluid_id, 0)
            )

        return allocate(self._fluid_input_requirements, capacities, accepts)

    def _item_output_template(self, index):
        template = self._item_output_templates.get(index)
        if template is None:
            output = self.outputs[CategoryType.ITEM][index][1]
            item = Item(output.id, output.aux, int(output.count))
            template = (item, item.GetBasicInfo().maxStackSize)
            self._item_output_templates[index] = template
        return template

    def plan_item_outputs(self, items, output_slots):
        entries = self.outputs.get(CategoryType.ITEM, [])
        allowed_slots = set(output_slots)
        requirements = _requirements(entries, int, True, allowed_slots)
        identities = [(element.id, element.aux) for _, element in entries]
        capacities = {slot: 0 for slot in allowed_slots}
        empty_slots = {slot for slot in allowed_slots if items.get(slot) is None}
        empty_capacities = {}
        accepted = set()
        for index, (slots, amount) in enumerate(requirements):
            if amount <= 0:
                continue
            template, max_stack = self._item_output_template(index)
            identity = identities[index]
            for slot in slots:
                current = items.get(slot)
                if current is None:
                    empty_capacities[(slot, identity)] = max_stack
                    capacities[slot] = max(capacities[slot], max_stack)
                elif template.CanMerge(current):
                    capacities[slot] = max(
                        capacities[slot], max(0, max_stack - current.count)
                    )
                else:
                    continue
                accepted.add((index, slot))

        def accepts(index, slot):
            return (index, slot) in accepted

        return allocate_outputs(
            requirements, capacities, accepts, identities, empty_slots,
            empty_capacities,
        )

    def plan_fluid_outputs(self, fluids, output_slots):
        entries = self.outputs.get(CategoryType.FLUID, [])
        allowed_slots = set(output_slots)
        requirements = _requirements(entries, float, True, allowed_slots)
        identities = [element.id for _, element in entries]
        capacities = {}
        empty_slots = set()
        for slot in allowed_slots:
            fluid = fluids[slot]
            # 无限储罐装满时不能用 inf - inf 计算剩余容量。
            capacities[slot] = (
                0 if fluid.volume >= fluid.max_volume
                else fluid.max_volume - fluid.volume
            )
            if fluid.fluid_id is None:
                empty_slots.add(slot)

        def accepts(index, slot):
            fluid = fluids[slot]
            return fluid.fluid_id is None or fluid.fluid_id == identities[index]

        return allocate_outputs(
            requirements, capacities, accepts, identities, empty_slots
        )


def get_recipe_plan(recipe):
    plan = getattr(recipe, "_processor_plan", None)
    signature = _recipe_signature(recipe)
    if (
        plan is None
        or plan.__class__ is not RecipePlan
        or plan.recipe is not recipe
        or getattr(plan, "_signature", None) != signature
    ):
        plan = recipe._processor_plan = RecipePlan(recipe, signature)
    return plan
