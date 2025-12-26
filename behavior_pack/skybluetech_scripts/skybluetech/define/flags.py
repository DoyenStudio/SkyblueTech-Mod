def mov(num):
    # type: (int) -> int
    return 1 << num

# general
DEACTIVE_FLAG_NO_RECIPE            = mov(1)
DEACTIVE_FLAG_OUTPUT_FULL          = mov(2)
DEACTIVE_FLAG_NO_INPUT             = mov(3)
DEACTIVE_FLAG_STRUCTURE_BROKEN     = mov(4)
DEACTIVE_FLAG_STRUCTURE_BLOCK_LACK = mov(5)

# appliance
DEACTIVE_FLAG_POWER_LACK           = mov(6)
DEACTIVE_FLAG_FLUID_NOT_MATCH      = mov(7)
DEACTIVE_FLAG_FLUID_FULL           = mov(8)

# generator
DEACTIVE_FLAG_POWER_FULL           = mov(6)


