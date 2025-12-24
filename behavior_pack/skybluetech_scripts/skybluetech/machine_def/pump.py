# coding=utf-8
#
M_AIR = 0
M_WATER = 1
M_LAVA = 2
M_OIL = 3

M_TYPE_MAPPING = {
    ("minecraft:water", 0): M_WATER,
    ("minecraft:flowing_water", 0): M_WATER,
    ("minecraft:lava", 0): M_LAVA,
    ("minecraft:flowing_lava", 0): M_LAVA,
    ("minecraft:oil_source_block", 0): M_OIL
}
M_TYPE_MAPPING_REVERSE = {v: k for k, v in M_TYPE_MAPPING.items()}

PUMP_FLUID_AND_POWER = {
    M_AIR: 0,
    M_WATER: 40,
    M_LAVA: 64,
    M_OIL: 56,
}
PUMP_SPEED = {
    M_AIR: 0,
    M_WATER: 125,
    M_LAVA: 100,
    M_OIL: 62,
}
