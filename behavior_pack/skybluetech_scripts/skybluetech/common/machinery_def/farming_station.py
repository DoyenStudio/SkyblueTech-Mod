# coding=utf-8

STORE_RF_MAX = 16000

# 果实不在植株本体上的作物（如南瓜苗、西瓜苗），不作为作物判定
FRUITLESS_CROPS = {
    "minecraft:pumpkin_stem",
    "minecraft:melon_stem",
}

# 原版带 growth 状态的作物成熟时的 growth 上限
# 其余带 growth 状态的方块一律按 growth=7 处理
COMMON_CROP_MAX_GROWTH = {
    "minecraft:wheat": 7,
    "minecraft:potatoes": 7,
    "minecraft:carrots": 7,
    "minecraft:beetroot": 7,
    "minecraft:sweet_berry_bush": 3,
    "minecraft:torchflower_crop": 1,
    "minecraft:pitcher_crop": 7,
}

FULL_BLOCK_CROPS = {
    "minecraft:melon_block",
    "minecraft:pumpkin",
}


def isCommonCrop(block_states):
    # type: (dict) -> bool
    return "growth" in block_states


def isArrisCrop(block_states):
    # type: (dict) -> bool
    return "arris:growth" in block_states


def isArrisCropRiped(block_states):
    # type: (dict) -> bool
    return block_states["arris:growth"] == 7


def isBlockCrop(block_name):
    return block_name in FULL_BLOCK_CROPS
