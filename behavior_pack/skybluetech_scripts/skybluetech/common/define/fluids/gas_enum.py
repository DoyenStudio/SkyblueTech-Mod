from ..id_enum import fluids

GAS = {
    fluids.METHANE,
    fluids.HYDROGEN,
}


def IsGas(block_name):
    # type: (str) -> bool
    return block_name in GAS
