COMMON_CONTAINERS = {
    "minecraft:chest",
    "minecraft:trapped_chest",
    "minecraft:barrel",
    "minecraft:hopper",
    "minecraft:shulker_box",
    "minecraft:crafter",
    "minecraft:dispenser",
    "minecraft:dropper",
}
SPECIAL_CONTAINERS = {
    "minecraft:furnace": ((0, 1), (2,)),
    "minecraft:blast_furnace": ((0, 1), (2,)),
    "minecraft:smoker": ((0, 1), (2,)),
}
# x++ = east  => 5
# x-- = west  => 4
# y++ = up    => 1
# y-- = down  => 0
# z++ = south => 3
# z-- = north => 2
FACING_ZHCN = {0: "下", 1: "上", 2: "北", 3: "南", 4: "西", 5: "东"}
FACING_EN = {0: "down", 1: "up", 2: "north", 3: "south", 4: "west", 5: "east"}
FACING_EN2NUM = {v: k for k, v in FACING_EN.items()}
DXYZ_FACING = {
    (0, 0, 1): 3,
    (0, 0, -1): 2,
    (0, 1, 0): 1,
    (0, -1, 0): 0,
    (1, 0, 0): 5,
    (-1, 0, 0): 4,
}
