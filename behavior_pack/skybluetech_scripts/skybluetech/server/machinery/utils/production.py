# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.skybluetech.common.mini_jei import CategoryType
from skybluetech_scripts.skybluetech.common.mini_jei.machinery import MachineRecipeBase  # noqa: F401
from skybluetech_scripts.skybluetech.common.define import flags

if 0>1:
    import typing  # noqa: F401
    from ..basic import BaseMachine  # noqa: F401

MISSING_TYPE = type("MISSING", (), {})
MISSING = MISSING_TYPE()


def MachineIsMatchInput(machine, recipe, cached_slotitems=None):
    # type: (BaseMachine, MachineRecipeBase, dict[int, Item | None] | None) -> bool
    """
    机器是否匹配配方输入。目前支持物品和流体容器的检测。

    Args:
        machine (BaseMachine): 机器基类
        recipe (MachineRecipeBase): 机器配方基类

    Returns:
        bool: 是否匹配输入
    """
    from ..basic import ItemContainer, FluidContainer, MultiFluidContainer

    if isinstance(machine, ItemContainer):
        input_items = recipe.GetMachineInputs().get(CategoryType.ITEM, {})
        for slot, item_input in input_items.items():
            if cached_slotitems is not None:
                machine_slot = cached_slotitems.get(slot, MISSING)
                if isinstance(machine_slot, MISSING_TYPE):
                    cached_slotitems[slot] = machine_slot = machine.GetSlotItem(
                        slot, get_user_data=True
                    )
            else:
                machine_slot = machine.GetSlotItem(slot, get_user_data=True)
            if machine_slot is None:
                return False
            elif machine_slot.id != item_input.id or machine_slot.count < int(
                item_input.count
            ):
                return False
    if isinstance(machine, FluidContainer):
        input_fluid = recipe.GetMachineInputs().get(CategoryType.FLUID, {}).get(0)
        if input_fluid is None:
            return False
        if (
            machine.fluid_id != input_fluid.id
            or machine.fluid_volume < input_fluid.count
        ):
            return False
    if isinstance(machine, MultiFluidContainer):
        input_fluids = recipe.GetMachineInputs().get(CategoryType.FLUID, {})
        for slot, input_fluid in input_fluids.items():
            if (
                machine.fluids[slot].fluid_id != input_fluid.id
                or machine.fluids[slot].volume < input_fluid.count
            ):
                return False
    return True


def MachineRecipeCanOutput(machine, recipe):
    # type: (BaseMachine, MachineRecipeBase) -> bool
    """
    配方产出能否不堵塞地输出到机器。目前支持物品和流体容器的检测。

    Args:
        machine (BaseMachine): 机器基类
        recipe (MachineRecipeBase): 机器配方基类

    Returns:
        bool: 是否可以输出
    """
    from ..basic import ItemContainer, FluidContainer, MultiFluidContainer

    if isinstance(machine, ItemContainer):
        output_items = recipe.GetMachineOutputs().get(CategoryType.ITEM, {})
        for slot, output in output_items.items():
            machine_slot = machine.GetSlotItem(slot, get_user_data=True)
            if machine_slot is None:
                continue
            elif not Item(output.id, count=int(output.count)).CanMerge(machine_slot):
                return False
            elif (
                machine_slot.count + int(output.count)
                > machine_slot.GetBasicInfo().maxStackSize
            ):
                return False
    if isinstance(machine, FluidContainer):
        output_fluid = recipe.GetMachineOutputs().get(CategoryType.FLUID, {}).get(0)
        if output_fluid is None:
            return False
        if (
            machine.fluid_id is not None and machine.fluid_id != output_fluid.id
        ) or machine.fluid_volume + output_fluid.count > machine.max_fluid_volume:
            return False
    elif isinstance(machine, MultiFluidContainer):
        output_fluids = recipe.GetMachineOutputs().get(CategoryType.FLUID, {})
        for slot, fluid in output_fluids.items():
            if (
                fluid.id is not None and fluid.id != machine.fluids[slot].fluid_id
            ) or machine.fluids[slot].volume + fluid.count > machine.fluids[
                slot
            ].max_volume:
                return False
    return True


def OutputRecipe(machine, recipe):
    # type: (BaseMachine, MachineRecipeBase) -> None
    """
    输出配方产出。目前支持物品和流体容器的输出。

    WARNING: 需要先使用 MachineRecipeCanOutput 检查配方是否可以产出！

    Args:
        machine (BaseMachine): 机器基类
        recipe (MachineRecipeBase): 机器配方基类
    """
    from ..basic import ItemContainer, FluidContainer, MultiFluidContainer

    if isinstance(machine, ItemContainer):
        output_items = recipe.GetMachineOutputs().get(CategoryType.ITEM, {})
        for slot, output in output_items.items():
            machine_slot = machine.GetSlotItem(slot, get_user_data=True)
            if machine_slot is None:
                machine.SetSlotItem(slot, Item(output.id, count=int(output.count)))
            else:
                machine_slot.count += int(output.count)
                machine.SetSlotItem(slot, machine_slot)
    if isinstance(machine, FluidContainer):
        output_fluid = recipe.GetMachineOutputs().get(CategoryType.FLUID, {}).get(0)
        if output_fluid is None:
            return
        machine.OutputFluid(output_fluid.id, output_fluid.count)
    elif isinstance(machine, MultiFluidContainer):
        output_fluids = recipe.GetMachineOutputs().get(CategoryType.FLUID, {})
        slots_and_fluids = output_fluids.items()
        last_index = len(slots_and_fluids) - 1
        for i, (slot, fluid) in enumerate(slots_and_fluids):
            if i == last_index:
                machine.OutputFluid(fluid.id, fluid.count, slot, is_final=True)
            else:
                machine.OutputFluid(fluid.id, fluid.count, slot, is_final=False)


def FlushRecipeStat(recipe, machine):
    # type: (MachineRecipeBase | None, BaseMachine) -> typing.TypeGuard[MachineRecipeBase]
    """
    刷新机器配方数据, 自动完成以下机器运行标志的设置:
        - DEACTIVE_FLAG_NO_RECIPE
        - DEACTIVE_FLAG_OUTPUT_FULL

    Args:
        machine (BaseMachine): 机器基类
        recipe (MachineRecipeBase | None): 机器配方基类

    Returns:
        bool: 目前配方是否有效
    """
    if recipe is None:
        machine.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
        return False
    else:
        machine.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
        if not MachineRecipeCanOutput(machine, recipe):
            machine.SetDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL)
            return False
        else:
            machine.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL)
            return True
