# coding=utf-8
"""气体冶金炉接口注册；控制器与加工逻辑另行实现。"""

from skybluetech_scripts.skybluetech.common.define.id_enum import GasMetallurgicalFurnace
from skybluetech_scripts.skybluetech.server.machinery.core import RegisterMachine
from skybluetech_scripts.skybluetech.server.machinery.interfaces import (
    EnergyInputInterface,
    FluidInputInterface,
    FluidOutputInterface,
    ItemInputInterface,
    ItemOutputInterface,
)


ItemInputInterface.AddExtraMachineId(GasMetallurgicalFurnace.IO_ITEM_INPUT)
ItemOutputInterface.AddExtraMachineId(GasMetallurgicalFurnace.IO_ITEM_OUTPUT)
FluidInputInterface.AddExtraMachineId(GasMetallurgicalFurnace.IO_GAS_INPUT)
FluidInputInterface.AddExtraMachineId(GasMetallurgicalFurnace.IO_GAS_INPUT_AUXILIARY)
FluidInputInterface.AddExtraMachineId(GasMetallurgicalFurnace.IO_FLUID_INPUT)
FluidOutputInterface.AddExtraMachineId(GasMetallurgicalFurnace.IO_GAS_OUTPUT)
FluidOutputInterface.AddExtraMachineId(GasMetallurgicalFurnace.IO_FLUID_OUTPUT)
EnergyInputInterface.AddExtraMachineId(GasMetallurgicalFurnace.IO_ENERGY_INPUT)

# 显式刷新接口注册表，不依赖尚未实现的控制器。
RegisterMachine(ItemInputInterface)
RegisterMachine(ItemOutputInterface)
RegisterMachine(FluidInputInterface)
RegisterMachine(FluidOutputInterface)
RegisterMachine(EnergyInputInterface)
