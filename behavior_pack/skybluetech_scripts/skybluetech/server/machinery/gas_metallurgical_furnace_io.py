# coding=utf-8
from ...common.define.id_enum import GasMetallurgicalFurnace as ids
from .basic.multiblock_processing_ports import MultiblockProcessingPorts
from .interfaces import (
    EnergyInputInterface, FluidInputInterface, FluidOutputInterface,
    ItemInputInterface, ItemOutputInterface,
)

PORTS = (
    (ids.IO_ENERGY_INPUT, EnergyInputInterface),
    (ids.IO_ITEM_INPUT, ItemInputInterface),
    (ids.IO_ITEM_OUTPUT, ItemOutputInterface),
    (ids.IO_GAS_INPUT, FluidInputInterface),
    (ids.IO_GAS_INPUT_AUXILIARY, FluidInputInterface),
    (ids.IO_FLUID_INPUT, FluidInputInterface),
    (ids.IO_GAS_OUTPUT, FluidOutputInterface),
    (ids.IO_FLUID_OUTPUT, FluidOutputInterface),
)
FLUID_INPUTS = ((ids.IO_GAS_INPUT, 0), (ids.IO_GAS_INPUT_AUXILIARY, 1), (ids.IO_FLUID_INPUT, 2))
FLUID_OUTPUTS = ((ids.IO_GAS_OUTPUT, 3), (ids.IO_FLUID_OUTPUT, 4))


class GasFurnaceIO(MultiblockProcessingPorts):
    ports = PORTS
    fluid_inputs_by_port = FLUID_INPUTS
    fluid_outputs_by_port = FLUID_OUTPUTS
    item_input_port = ids.IO_ITEM_INPUT
    item_output_port = ids.IO_ITEM_OUTPUT
